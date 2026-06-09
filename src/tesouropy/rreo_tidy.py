"""RREO tidy layer — handles SICONFI's drifting labels across years.

SICONFI's RREO appendix names, account labels, and column suffixes drift across
fiscal years. The package ships a small reference table
(``data/rreo_layout.csv``) mapping ``(topic, regime, year_range)`` to the
correct appendix and account-matching key, and uses it to assemble
layout-stable indicators across years.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from importlib import resources

import polars as pl

from ._core import TesouroError

__all__ = ["rreo_layout", "rreo_normalize_columns", "tidy_rreo"]

_YEAR_SUFFIX_RE = re.compile(r"(\s*/\s*\d{4}|\s+EM\s+\d{4})\s*$")
_TRAILING_YEAR_RE = re.compile(r"(\d{4})\s*$")


def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _clean_conta(value: str) -> str:
    """Reduce a SICONFI ``conta`` value to a stable matching key.

    Drops everything from the first ``(`` (formula notation with Roman numerals
    that drift across years), strips diacritics, lowercases and squishes
    whitespace.
    """
    value = re.sub(r"\s*\(.*$", "", value or "")
    value = _strip_accents(value)
    value = value.lower()
    return re.sub(r"\s+", " ", value).strip()


@lru_cache(maxsize=1)
def _load_rreo_layout() -> pl.DataFrame:
    with resources.as_file(
        resources.files("tesouropy").joinpath("data/rreo_layout.csv")
    ) as path:
        tbl = pl.read_csv(path)
    return tbl.with_columns(
        pl.col("first_year").cast(pl.Int64),
        pl.col("last_year").cast(pl.Int64),
    )


def rreo_layout() -> pl.DataFrame:
    """Return the bundled RREO layout reference table.

    Columns: ``topic``, ``regime``, ``first_year``, ``last_year``,
    ``co_esfera``, ``no_anexo``, ``conta_match``, ``indicador``.
    """
    return _load_rreo_layout()


def rreo_normalize_columns(data: pl.DataFrame) -> pl.DataFrame:
    """Normalize the ``coluna`` field of an RREO DataFrame across years.

    Appends two columns:

    * ``coluna_padrao``: the column label with any trailing ``/ YYYY`` or
      ``EM YYYY`` suffix removed (whitespace squished).
    * ``coluna_ano``: the year that appeared in the suffix (Int64), or null when
      no year was present.
    """
    if "coluna" not in data.columns:
        raise TesouroError("Input must have a `coluna` column.")

    colunas = data["coluna"].to_list()
    anos: list[int | None] = []
    padroes: list[str] = []
    for value in colunas:
        value = value if value is not None else ""
        if _YEAR_SUFFIX_RE.search(value):
            match = _TRAILING_YEAR_RE.search(value)
            anos.append(int(match.group(1)) if match else None)
        else:
            anos.append(None)
        padrao = _YEAR_SUFFIX_RE.sub("", value)
        padroes.append(re.sub(r"\s+", " ", padrao).strip())

    return data.with_columns(
        pl.Series("coluna_padrao", padroes),
        pl.Series("coluna_ano", anos, dtype=pl.Int64),
    )


def tidy_rreo(data: pl.DataFrame, topic: str, regime=None) -> pl.DataFrame:
    """Tidy an RREO DataFrame by topic, reconciling layout drift across years.

    Filters ``data`` (typically from :func:`tesouropy.get_rreo`) to the rows
    matching a known indicator for ``topic`` (and optionally ``regime``), using
    the rules in :func:`rreo_layout`. Accounts are matched on a year-stable,
    accent-folded key, so the same call returns a coherent series across years
    even when SICONFI relabelled the appendix or account.

    Currently supported topics: ``"previdencia"`` (federal RGPS / RPPS civis /
    FCDF / militares inativos, União sphere).
    """
    required = ("exercicio", "conta", "coluna", "valor")
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise TesouroError(
            f"Input is missing required column(s): {', '.join(missing)}. "
            "Did you pass the raw output of get_rreo()?"
        )

    layout = _load_rreo_layout().filter(pl.col("topic") == topic)
    if regime is not None:
        regimes = [regime] if isinstance(regime, str) else list(regime)
        layout = layout.filter(pl.col("regime").is_in(regimes))
    if layout.height == 0:
        extra = "" if regime is None else f", regime={regime}"
        raise TesouroError(
            f"No layout entry for topic={topic!r}{extra}. Run rreo_layout() to "
            "inspect supported topics/regimes."
        )

    data = rreo_normalize_columns(data)
    data = data.with_columns(
        pl.col("conta")
        .map_elements(_clean_conta, return_dtype=pl.Utf8)
        .alias("_match_key"),
        pl.col("exercicio").cast(pl.Int64, strict=False).alias("_exercicio"),
    )

    matched = []
    for rule in layout.iter_rows(named=True):
        rows = data.filter(
            pl.col("_exercicio").is_not_null()
            & (pl.col("_exercicio") >= rule["first_year"])
            & (pl.col("_exercicio") <= rule["last_year"])
            & (pl.col("_match_key") == rule["conta_match"])
        )
        if rows.height:
            rows = rows.with_columns(
                pl.lit(rule["indicador"]).alias("indicador"),
                pl.lit(rule["regime"]).alias("regime"),
            )
            matched.append(rows)

    if not matched:
        # warn-and-return-empty, mirroring the R behaviour
        import logging

        logging.getLogger("tesouropy").warning(
            "No rows matched topic=%r in the supplied data.", topic
        )
        return pl.DataFrame()

    result = pl.concat(matched, how="diagonal_relaxed").drop(
        "_match_key", "_exercicio"
    )

    lead = ["indicador", "regime"]
    for col in ("exercicio", "instituicao", "cod_ibge", "uf"):
        if col in result.columns:
            lead.append(col)
    rest = [c for c in result.columns if c not in lead]
    return result.select(lead + rest)
