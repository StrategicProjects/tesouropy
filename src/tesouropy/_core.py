"""Internal HTTP, caching, pagination and tidy infrastructure for tesouropy.

This mirrors ``R/utils.R`` of the original ``tesouror`` R package. All the
network plumbing lives here; the per-API modules are thin wrappers that build
parameters and delegate to the helpers below.

Nothing in this module is part of the public API (names are prefixed or kept
out of ``tesouropy.__init__``), with the single exception of
:func:`tesouropy_clear_cache`.
"""

from __future__ import annotations

import logging
import re
import time
import unicodedata
from typing import Any, Callable, Iterable, Mapping, Sequence

import polars as pl
import requests

__all__ = ["tesouropy_clear_cache", "TesouroError", "set_verbose"]

log = logging.getLogger("tesouropy")
# Library code should not configure the root logger; emit through a NullHandler
# so importing tesouropy is silent unless the user opts in to logging.
log.addHandler(logging.NullHandler())

INF = float("inf")


class TesouroError(RuntimeError):
    """Raised for actionable errors talking to a Treasury API."""


# -- Verbose helper -----------------------------------------------------------

_VERBOSE_DEFAULT = False


def set_verbose(value: bool) -> None:
    """Set the package-wide default for the ``verbose`` argument.

    Equivalent to ``options(tesouror.verbose = TRUE)`` in the R package.
    """
    global _VERBOSE_DEFAULT
    _VERBOSE_DEFAULT = bool(value)


def is_verbose(verbose: bool | None) -> bool:
    if verbose is None:
        return _VERBOSE_DEFAULT
    return bool(verbose) or _VERBOSE_DEFAULT


# -- Parameter validation -----------------------------------------------------


def check_required(**kwargs: Any) -> None:
    """Abort with a clear message if any required argument is ``None``.

    Python already raises ``TypeError`` for missing positional arguments; this
    guards against callers explicitly passing ``None`` to a required parameter.
    """
    missing = [name for name, val in kwargs.items() if val is None]
    if missing:
        plural = "s" if len(missing) > 1 else ""
        names = ", ".join(f"`{m}`" for m in missing)
        raise TesouroError(f"Missing required argument{plural}: {names}.")


# -- Parameter collapsing -----------------------------------------------------


def collapse_param(x: Any) -> str | None:
    """Collapse a scalar or sequence into a colon-separated string.

    Mirrors ``collapse_param`` in R: ``c(1, 2, 3)`` -> ``"1:2:3"``. A scalar is
    returned as-is (stringified); ``None`` stays ``None`` so the parameter is
    dropped from the query.
    """
    if x is None:
        return None
    if isinstance(x, str):
        return x
    if isinstance(x, (list, tuple, set)):
        return ":".join(str(v) for v in x)
    return str(x)


# -- UF abbreviation guard ----------------------------------------------------

UF_ABBREVS = frozenset(
    {
        "AC", "AL", "AM", "AP", "BA", "BR", "CE", "DF", "ES", "GO",
        "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ",
        "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
    }
)


def check_not_uf_abbrev(value: Any, arg_name: str) -> None:
    """Abort if a two-letter UF abbreviation is passed where a numeric Treasury
    state code is expected.

    Several Transferencias endpoints expect a numeric Treasury state code (NOT
    the IBGE code and NOT the two-letter abbreviation). Passing the
    abbreviation makes the upstream API return HTTP 500 after a long retry
    budget; this short-circuits that with an actionable error.
    """
    if value is None:
        return
    if isinstance(value, (list, tuple, set)):
        return
    v = str(value)
    if len(v) == 2 and v.upper() in UF_ABBREVS:
        raise TesouroError(
            f"`{arg_name}` must be a Treasury state code (numeric), not the UF "
            f"abbreviation {v!r}. Look it up with get_tc_estados(): e.g. "
            'estados.filter(pl.col("nome") == "Pernambuco")["codigo"].'
        )


# -- SIORG code padding -------------------------------------------------------


def pad_siorg_code(code: Any) -> str | None:
    """Pad a SIORG code to 6 digits with leading zeros (``244`` -> ``"000244"``)."""
    if code is None:
        return None
    return f"{int(code):06d}"


# -- Base URLs ----------------------------------------------------------------

SICONFI_BASE_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
CUSTOS_BASE_URL = "https://apidatalake.tesouro.gov.br/ords/custos/tt"
SADIPEM_BASE_URL = "https://apidatalake.tesouro.gov.br/ords/sadipem/tt/"
TRANSFERENCIAS_BASE_URL = (
    "https://apiapex.tesouro.gov.br/aria/v1/transferencias_constitucionais/custom"
)
SIORG_BASE_URL = "https://estruturaorganizacional.dados.gov.br"
SIOPE_BASE_URL = (
    "https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata"
)


# -- In-memory cache ----------------------------------------------------------

_CACHE: dict[str, Any] = {}


def _cache_key(url: str, params: Mapping[str, Any]) -> str:
    parts = [url] + sorted(f"{k}={v}" for k, v in params.items())
    return "|".join(parts)


def tesouropy_clear_cache() -> None:
    """Clear the tesouropy in-memory cache.

    Removes **all** cached API responses stored during the current session.
    This applies to every API covered by the package (SICONFI, CUSTOS,
    SADIPEM, Transferencias, SIORG, SIOPE): they share a single in-memory store.
    """
    _CACHE.clear()
    log.info("Cache cleared (all APIs).")


# -- Name cleaning (janitor::clean_names analogue) ----------------------------

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _strip_accents(text: str) -> str:
    """Transliterate accented characters to ASCII (``"ção"`` -> ``"cao"``)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def clean_name(name: str) -> str:
    """Convert a single column name to snake_case, accent-folded form."""
    name = _strip_accents(str(name))
    name = _CAMEL_RE.sub("_", name)
    name = name.lower()
    name = _NON_ALNUM_RE.sub("_", name)
    name = name.strip("_")
    return name


def clean_names(df: pl.DataFrame) -> pl.DataFrame:
    """Clean all column names of a polars DataFrame to unique snake_case.

    Mirrors ``janitor::clean_names()``: transliterate accents, split camelCase,
    lowercase, replace runs of non-alphanumeric characters with ``_``, and
    de-duplicate by appending ``_2``, ``_3`` ... to repeats.
    """
    seen: dict[str, int] = {}
    mapping: dict[str, str] = {}
    for col in df.columns:
        cleaned = clean_name(col) or "x"
        if cleaned in seen:
            seen[cleaned] += 1
            cleaned = f"{cleaned}_{seen[cleaned]}"
        else:
            seen[cleaned] = 1
        mapping[col] = cleaned
    return df.rename(mapping)


def _squish_strings(df: pl.DataFrame) -> pl.DataFrame:
    """Trim and collapse internal whitespace on all string columns."""
    string_cols = [c for c, dt in zip(df.columns, df.dtypes) if dt == pl.Utf8]
    if not string_cols:
        return df
    return df.with_columns(
        pl.col(c).str.strip_chars().str.replace_all(r"\s+", " ") for c in string_cols
    )


def _from_records(records: Sequence[Mapping[str, Any]]) -> pl.DataFrame:
    """Build a polars DataFrame from a list of dicts, tolerating ragged keys."""
    return pl.from_dicts(list(records), infer_schema_length=None)


def _empty() -> pl.DataFrame:
    return pl.DataFrame()


def _attach(df: pl.DataFrame, **meta: Any) -> pl.DataFrame:
    """Attach metadata (``partial``, ``failed`` ...) as instance attributes.

    The polars analogue of R's ``attr(result, ...)``. These attributes are best
    consumed immediately after the call; most polars operations return a fresh
    DataFrame that will not carry them over.
    """
    for key, value in meta.items():
        try:
            setattr(df, key, value)
        except (AttributeError, TypeError):  # pragma: no cover - defensive
            pass
    return df


# -- Request builder ----------------------------------------------------------

MAX_RETRIES = 5
RETRY_WAIT = 3
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})

_SESSION = requests.Session()


def _sleep(seconds: float) -> None:
    """Indirection so tests can monkeypatch the backoff delay."""
    time.sleep(seconds)


def _build_display_url(url: str, params: Mapping[str, Any]) -> str:
    clean = {k: v for k, v in params.items() if v is not None}
    if not clean:
        return url
    query = "&".join(f"{k}={v}" for k, v in clean.items())
    return f"{url}?{query}"


def tnr_request(
    url: str,
    params: Mapping[str, Any] | None = None,
    *,
    use_cache: bool = True,
    api_name: str = "Treasury",
    accept: str = "application/json",
    verbose: bool | None = False,
    timeout: float = 60.0,
) -> Any:
    """Build and perform a single request to a Treasury API.

    Handles the in-memory cache (checked before, written after), retries (5
    attempts with progressive 3/6/9/12s backoff on 5xx/429 and connection
    failures), and actionable error messages. Returns the parsed JSON body.
    """
    params = {k: v for k, v in (params or {}).items() if v is not None}

    if is_verbose(verbose):
        log.info("API call: %s", _build_display_url(url, params))

    key = None
    if use_cache:
        key = _cache_key(url, params)
        if key in _CACHE:
            return _CACHE[key]

    headers = {"Accept": accept}
    resp: requests.Response | None = None
    last_error: Exception | None = None
    last_status: int | None = None
    attempt = 0

    for attempt in range(1, MAX_RETRIES + 1):
        last_error = None
        last_status = None
        try:
            resp = _SESSION.get(url, params=params, headers=headers, timeout=timeout)
        except requests.RequestException as exc:
            last_error = exc
            resp = None

        if resp is not None:
            last_status = resp.status_code
            if last_status == 200:
                break
            if last_status in RETRYABLE_STATUSES:
                if attempt < MAX_RETRIES:
                    wait = RETRY_WAIT * attempt
                    log.warning(
                        "HTTP %s on attempt %s/%s. Retrying in %ss...",
                        last_status, attempt, MAX_RETRIES, wait,
                    )
                    _sleep(wait)
                    resp = None
                    continue
                # last attempt failed with retryable status -> fall through
            else:
                break  # non-retryable HTTP error
        else:
            if attempt < MAX_RETRIES:
                wait = RETRY_WAIT * attempt
                log.warning(
                    "Connection failed (attempt %s/%s). Retrying in %ss...",
                    attempt, MAX_RETRIES, wait,
                )
                _sleep(wait)

    # All retries exhausted with a connection failure
    if resp is None:
        err_msg = str(last_error) if last_error is not None else "Unknown error"
        hint = _connection_hint(err_msg)
        bullets = [
            f"Failed to connect to the {api_name} API after {MAX_RETRIES} attempts.",
            f"URL: {url}",
        ]
        if hint:
            bullets.append(hint)
        bullets.append(f"Original error: {err_msg}")
        bullets.append("Try again later or check your internet connection.")
        raise TesouroError("\n".join(bullets))

    status = resp.status_code
    if status != 200:
        detail = _error_detail(resp)
        hint = _status_hint(status, api_name, detail)
        retry_note = f" (after {attempt} attempts)" if attempt > 1 else ""
        raise TesouroError(
            f"{api_name} API returned HTTP status {status}{retry_note}.\n"
            f"URL: {_build_display_url(url, params)}\n{hint}"
        )

    try:
        body = resp.json()
    except ValueError as exc:
        raise TesouroError(
            f"Failed to parse the API response as JSON.\nURL: {url}\n"
            f"Original error: {exc}"
        ) from exc

    if use_cache and key is not None:
        _CACHE[key] = body
    return body


def _connection_hint(err_msg: str) -> str | None:
    low = err_msg.lower()
    if re.search(r"http/2|stream|protocol_error", low):
        return "The server closed the connection unexpectedly (HTTP/2 protocol error)."
    if re.search(r"resolve|dns|getaddrinfo|name or service", low):
        return "Could not resolve the API hostname. Check your internet connection."
    if re.search(r"time.?out", low):
        return "The request timed out. The API may be temporarily unavailable."
    if "refused" in low:
        return "Connection refused by the server."
    if re.search(r"ssl|certificate|tls", low):
        return "SSL/TLS error. There may be a network or certificate issue."
    return None


def _error_detail(resp: requests.Response) -> str | None:
    try:
        body = resp.json()
    except ValueError:
        return None
    if not isinstance(body, Mapping):
        return None
    err = body.get("error")
    if isinstance(err, Mapping):
        msg = err.get("message")
        if isinstance(msg, str):
            return msg
    msg = body.get("message")
    if isinstance(msg, str):
        return msg
    if isinstance(err, str):
        return err
    return None


def _status_hint(status: int, api_name: str, detail: str | None) -> str:
    if status == 400:
        if detail:
            return f"Bad request. Server message: {detail}"
        return (
            "Bad request. If using filter, select, or orderby: check that "
            "column names match the original API names (uppercase). Use "
            "verbose=True with max_rows=1 to inspect valid column names."
        )
    if status == 404:
        return "The endpoint or entity was not found. Check your parameters."
    if status in (502, 503, 504):
        if api_name == "CUSTOS":
            return (
                "Server timeout. The CUSTOS backend is slow on broad queries. "
                "Try (a) adding a `mes` filter (e.g. mes=6) and/or (b) reducing "
                "page_size (e.g. 250). If pagination fails mid-way, the package "
                "returns a partial result with result.partial == True."
            )
        return "Server timeout. Try a smaller page_size or retry later."
    if status >= 500:
        return "Server error. The API may be temporarily unavailable."
    if status == 429:
        return "Rate limited. Wait a moment before retrying."
    return "Check your parameters and try again."


# -- Pagination (ORDS-style) --------------------------------------------------


def _resolve_max_rows(max_rows: float | int | None) -> float:
    if max_rows is None:
        return INF
    return float(max_rows)


def ords_fetch_all(
    base_url: str,
    endpoint: str,
    params: Mapping[str, Any] | None = None,
    *,
    use_cache: bool = True,
    api_name: str = "Treasury",
    verbose: bool | None = False,
    page_size: int | None = None,
    max_rows: float | int | None = INF,
) -> pl.DataFrame:
    """Page an ORDS endpoint (SICONFI/CUSTOS/SADIPEM) following ``hasMore``.

    Fault tolerant: if a page after the first fails, the partial DataFrame is
    returned with ``result.partial == True`` and ``result.last_page_error`` set,
    instead of discarding what was already fetched.
    """
    params = dict(params or {})
    max_rows_f = _resolve_max_rows(max_rows)
    url = base_url + endpoint

    if page_size is not None:
        params["limit"] = int(page_size)
    if max_rows_f != INF:
        if params.get("limit") is not None:
            params["limit"] = min(int(params["limit"]), int(max_rows_f))
        else:
            params["limit"] = int(max_rows_f)

    all_items: list[Mapping[str, Any]] = []
    page = 1
    total_rows = 0

    log.info("Fetching %s%s page %s...", api_name, endpoint, page)
    body = tnr_request(
        url, params, use_cache=use_cache, api_name=api_name, verbose=verbose
    )
    items = body.get("items") if isinstance(body, Mapping) else None

    if not items:
        log.warning("No data returned for %s%s.", api_name, endpoint)
        return _empty()

    all_items.extend(items)
    total_rows += len(items)
    has_more = bool(body.get("hasMore"))
    log.info("%s%s | page %s | %s rows", api_name, endpoint, page, total_rows)

    partial_error: str | None = None
    while has_more and total_rows < max_rows_f:
        page += 1
        offset = body.get("offset")
        limit = body.get("limit")
        if offset is None or limit is None:
            break
        next_params = dict(params)
        next_params["offset"] = offset + limit

        log.info("Fetching %s%s page %s...", api_name, endpoint, page)
        try:
            body = tnr_request(
                url, next_params, use_cache=use_cache, api_name=api_name,
                verbose=verbose,
            )
        except TesouroError as exc:
            partial_error = str(exc)
            log.warning(
                "Page %s failed; returning partial result of %s rows from %s "
                "page(s).", page, total_rows, page - 1,
            )
            page -= 1
            break

        items = body.get("items") if isinstance(body, Mapping) else None
        if not items:
            break
        all_items.extend(items)
        total_rows += len(items)
        has_more = bool(body.get("hasMore"))
        log.info("%s%s | page %s | %s rows", api_name, endpoint, page, total_rows)

    result = _from_records(all_items)
    result = _squish_strings(result)
    result = clean_names(result)

    if max_rows_f != INF and result.height > max_rows_f:
        result = result.head(int(max_rows_f))
        log.info("Done: %s rows (truncated to max_rows).", result.height)
    elif partial_error is not None:
        log.warning("Done (PARTIAL): %s rows from %s page(s).", result.height, page)
    else:
        log.info("Done: %s rows total (%s page(s)).", result.height, page)

    if partial_error is not None:
        _attach(result, partial=True, last_page_error=partial_error)
    return result


# -- Looped fetch with fault tolerance ----------------------------------------


def tnr_loop(
    func: Callable[..., pl.DataFrame],
    param_list: Sequence[Mapping[str, Any]],
    *,
    id_key: str | None = None,
    on_error: str = "warn",
    progress_label: str = "Iteration",
) -> pl.DataFrame:
    """Apply ``func`` across many parameter sets, tolerating per-call failures.

    Iterations that raise are recorded in ``result.failed`` (a DataFrame with
    ``iteration``, ``id``, ``error``); iterations that succeed but return zero
    rows are recorded in ``result.no_data``.
    """
    if on_error not in ("warn", "stop", "silent"):
        raise TesouroError("on_error must be one of 'warn', 'stop', 'silent'.")

    n = len(param_list)
    results: list[pl.DataFrame | None] = [None] * n
    failures: list[dict[str, Any]] = []
    empties: list[dict[str, Any]] = []

    def label_of(i: int) -> str:
        args = param_list[i]
        if id_key is not None and args.get(id_key) is not None:
            return str(args[id_key])
        return str(i + 1)

    log.info("%s: looping over %s call(s)...", progress_label, n)

    for i in range(n):
        args = dict(param_list[i])
        label = label_of(i)
        try:
            res = func(**args)
        except TesouroError as exc:
            failures.append({"iteration": i + 1, "id": label, "error": str(exc)})
            if on_error == "stop":
                raise
            if on_error == "warn":
                log.warning(
                    "[%s/%s] %s %s failed: %s", i + 1, n, progress_label, label, exc
                )
            continue

        if isinstance(res, pl.DataFrame) and res.height == 0:
            empties.append({"iteration": i + 1, "id": label})
        else:
            results[i] = res

    ok = [r for r in results if r is not None]
    combined = pl.concat(ok, how="diagonal_relaxed") if ok else _empty()

    n_failed = len(failures)
    n_empty = len(empties)
    n_ok = n - n_failed - n_empty

    meta: dict[str, Any] = {}
    if n_failed:
        meta["failed"] = _from_records(failures)
        if on_error != "silent":
            log.warning(
                "%s of %s call(s) failed. Inspect with result.failed.", n_failed, n
            )
    if n_empty:
        meta["no_data"] = _from_records(empties)
        if on_error != "silent":
            log.info(
                "%s of %s call(s) returned no data. Inspect with result.no_data.",
                n_empty, n,
            )
    if not n_failed and not n_empty:
        log.info("All %s call(s) succeeded.", n)
    elif not n_failed:
        log.info("%s of %s call(s) returned data.", n_ok, n)

    if meta:
        _attach(combined, **meta)
    return combined


# -- Convenience wrappers per API ---------------------------------------------


def siconfi_fetch_all(endpoint, params=None, *, use_cache=True, verbose=False,
                      page_size=None, max_rows=INF):
    return ords_fetch_all(
        SICONFI_BASE_URL, endpoint, params, use_cache=use_cache,
        api_name="SICONFI", verbose=verbose, page_size=page_size,
        max_rows=max_rows,
    )


def custos_fetch_all(endpoint, params=None, *, use_cache=True, verbose=False,
                     page_size=500, max_rows=INF):
    return ords_fetch_all(
        CUSTOS_BASE_URL, endpoint, params, use_cache=use_cache,
        api_name="CUSTOS", verbose=verbose, page_size=page_size,
        max_rows=max_rows,
    )


def sadipem_fetch_all(endpoint, params=None, *, use_cache=True, verbose=False,
                      page_size=None, max_rows=INF):
    return ords_fetch_all(
        SADIPEM_BASE_URL, endpoint, params, use_cache=use_cache,
        api_name="SADIPEM", verbose=verbose, page_size=page_size,
        max_rows=max_rows,
    )


# -- Transferencias fetch -----------------------------------------------------


def transferencias_fetch(endpoint, params=None, *, use_cache=True, verbose=False):
    url = TRANSFERENCIAS_BASE_URL + endpoint
    log.info("Fetching Transferencias%s...", endpoint)
    body = tnr_request(
        url, params, use_cache=use_cache, api_name="Transferencias",
        accept="*/*", verbose=verbose,
    )

    if isinstance(body, list):
        items = body
    elif isinstance(body, Mapping):
        items = body.get("registros") or body.get("items") or None
        if items is None:
            # A bare object response: treat as a single record.
            items = [body] if body else None
    else:
        items = None

    if not items:
        log.warning("No data returned for Transferencias%s.", endpoint)
        return _empty()

    result = _from_records(items)
    result = _squish_strings(result)
    result = clean_names(result)
    log.info("Done: %s rows.", result.height)
    return result


# -- SIOPE fetch (OData-style) ------------------------------------------------


def siope_build_url(resource: str, params: Mapping[str, Any]) -> tuple[str, dict]:
    """Build an OData URL + query dict for the SIOPE API.

    Pattern: ``Resource(P1=@P1,P2=@P2)?@P1=value&$format=json``.
    """
    aliases = ",".join(f"{k}=@{k}" for k in params)
    segment = f"{resource}({aliases})"
    query: dict[str, Any] = {}
    for k, v in params.items():
        query[f"@{k}"] = f"'{v}'" if isinstance(v, str) else v
    query["$format"] = "json"
    url = f"{SIOPE_BASE_URL}/{segment}"
    return url, query


_NUMERIC_RE = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")


def siope_items_to_frame(items: Any, resource: str) -> pl.DataFrame:
    """Parse OData ``value`` items into a DataFrame with safe type handling.

    OData responses often mix types across rows for the same field, so we read
    everything as text first, then cast numeric-looking columns to Float64.
    """
    if not items:
        return _empty()
    try:
        records = [
            {k: (None if v is None else str(v)) for k, v in row.items()}
            for row in items
        ]
        tbl = _from_records(records)
    except Exception as exc:  # pragma: no cover - defensive
        raise TesouroError(
            f"Failed to parse SIOPE response into a DataFrame.\n"
            f"Resource: {resource}\nOriginal error: {exc}"
        ) from exc

    cast_exprs = []
    for col, dt in zip(tbl.columns, tbl.dtypes):
        if dt != pl.Utf8:
            continue
        non_null = tbl[col].drop_nulls()
        if non_null.len() > 0 and all(_NUMERIC_RE.match(v) for v in non_null):
            cast_exprs.append(pl.col(col).cast(pl.Float64, strict=False))
    if cast_exprs:
        tbl = tbl.with_columns(cast_exprs)
    return tbl


def siope_fetch(resource, params=None, *, use_cache=True, verbose=False,
                page_size=1000, max_rows=INF, filter=None, orderby=None,
                select=None):
    params = dict(params or {})
    url, query = siope_build_url(resource, params)

    if filter is not None:
        query["$filter"] = filter
    if orderby is not None:
        query["$orderby"] = orderby
    if select is not None:
        query["$select"] = ",".join(select) if isinstance(select, (list, tuple)) else select

    max_rows_f = _resolve_max_rows(max_rows)
    effective_top = int(page_size)
    if max_rows_f != INF and max_rows_f < effective_top:
        effective_top = int(max_rows_f)
    query["$top"] = effective_top

    all_frames: list[pl.DataFrame] = []
    page = 1
    total_rows = 0

    log.info("Fetching SIOPE/%s page %s...", resource, page)
    if is_verbose(verbose):
        log.info("API call: %s", _build_display_url(url, query))
    body = tnr_request(url, query, use_cache=use_cache, api_name="SIOPE")
    items = body.get("value") if isinstance(body, Mapping) else None
    if not items:
        log.warning("No data returned for SIOPE/%s.", resource)
        return _empty()

    page_tbl = siope_items_to_frame(items, resource)
    all_frames.append(page_tbl)
    total_rows += page_tbl.height
    log.info("SIOPE/%s | page %s | %s rows", resource, page, total_rows)

    while page_tbl.height >= effective_top and total_rows < max_rows_f:
        page += 1
        query["$skip"] = total_rows
        if max_rows_f != INF:
            remaining = int(max_rows_f - total_rows)
            query["$top"] = min(effective_top, remaining)

        log.info("Fetching SIOPE/%s page %s...", resource, page)
        if is_verbose(verbose):
            log.info("API call: %s", _build_display_url(url, query))
        body = tnr_request(url, query, use_cache=use_cache, api_name="SIOPE")
        items = body.get("value") if isinstance(body, Mapping) else None
        if not items:
            break
        page_tbl = siope_items_to_frame(items, resource)
        all_frames.append(page_tbl)
        total_rows += page_tbl.height
        log.info("SIOPE/%s | page %s | %s rows", resource, page, total_rows)

    result = pl.concat(all_frames, how="diagonal_relaxed") if all_frames else _empty()
    result = _squish_strings(result)
    result = clean_names(result)

    if max_rows_f != INF and result.height > max_rows_f:
        result = result.head(int(max_rows_f))
        log.info("Done: %s rows (truncated to max_rows).", result.height)
    else:
        log.info("Done: %s rows total (%s page(s)).", result.height, page)
    return result


# -- State municipality resolver ----------------------------------------------


def resolve_state_munis(state_uf, *, include_capital=True, use_cache=True,
                        verbose=False):
    """Return municipalities of a Brazilian state for SICONFI loops."""
    from .siconfi import get_entes

    entes = get_entes(use_cache=use_cache, verbose=verbose)
    munis = entes.filter(
        (pl.col("uf") == state_uf) & (pl.col("esfera") == "M")
    )
    if not include_capital and "capital" in munis.columns:
        munis = munis.filter(pl.col("capital") != 1)
    if munis.height == 0:
        raise TesouroError(
            f"No municipalities found for {state_uf!r}. Check the UF code or "
            "run get_entes() to inspect available states."
        )
    return munis
