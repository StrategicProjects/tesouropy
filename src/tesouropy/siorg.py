"""SIORG API functions (federal organizational structure).

API docs: https://api.siorg.economia.gov.br/
Base URL: https://estruturaorganizacional.dados.gov.br

SIORG codes are used as the ``organizacao_n1/n2/n3`` parameters in the CUSTOS
API. The API returns identifiers as URIs (e.g.
``https://.../id/unidade-organizacional/46``); the numeric tail is extracted
for ease of use.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

import polars as pl

from ._core import (
    SIORG_BASE_URL,
    TesouroError,
    check_required,
    clean_names,
    tnr_request,
)

__all__ = [
    "get_siorg_orgaos", "get_siorg_organizations",
    "get_siorg_estrutura", "get_siorg_structure",
    "get_siorg_unidade", "get_siorg_unit",
]

log = logging.getLogger("tesouropy")

_URI_COLS = (
    "codigoUnidade", "codigoUnidadePai", "codigoOrgaoEntidade",
    "codigoTipoUnidade", "codigoEsfera", "codigoPoder",
    "codigoNaturezaJuridica", "codigoSubNaturezaJuridica",
    "codigoCategoriaUnidade",
)


def _extract_siorg_code(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    return text.rsplit("/", 1)[-1]


def _siorg_fetch(path, params=None, *, use_cache=True, verbose=False):
    url = f"{SIORG_BASE_URL}{path}.json"
    log.info("Fetching SIORG%s...", path)
    body = tnr_request(url, params, use_cache=use_cache, api_name="SIORG",
                       verbose=verbose)
    if isinstance(body, Mapping):
        servico = body.get("servico")
        if isinstance(servico, Mapping) and servico.get("codigoErro") not in (None, 0):
            raise TesouroError(
                f"SIORG API returned error code {servico.get('codigoErro')}. "
                f"Message: {servico.get('mensagem')}"
            )
    return body


def _parse_unidades(body) -> pl.DataFrame:
    unidades = body.get("unidades") if isinstance(body, Mapping) else None
    if not unidades:
        return pl.DataFrame()
    records = []
    for row in unidades:
        rec = dict(row)
        for col in _URI_COLS:
            if col in rec:
                rec[col] = _extract_siorg_code(rec[col])
        records.append(rec)
    result = pl.from_dicts(records, infer_schema_length=None)
    result = clean_names(result)
    string_cols = [c for c, dt in zip(result.columns, result.dtypes) if dt == pl.Utf8]
    if string_cols:
        result = result.with_columns(
            pl.col(c).str.strip_chars().str.replace_all(r"\s+", " ")
            for c in string_cols
        )
    return result


def get_siorg_orgaos(codigo_poder=None, codigo_esfera=None, use_cache=True,
                     verbose=False):
    """Get federal organizations (organs and entities) from SIORG.

    ``codigo_poder``: ``1`` Executive, ``2`` Legislative, ``3`` Judiciary.
    ``codigo_esfera``: ``1`` Federal, ``2`` State/District, ``3`` Municipal.
    Use the returned ``codigo_unidade`` as ``organizacao_n1`` in CUSTOS.
    """
    params = {"codigoPoder": codigo_poder, "codigoEsfera": codigo_esfera}
    body = _siorg_fetch("/doc/orgao-entidade/resumida", params,
                        use_cache=use_cache, verbose=verbose)
    result = _parse_unidades(body)
    if result.height == 0:
        log.warning("No organizations returned from SIORG.")
        return pl.DataFrame()
    log.info("Done: %s organizations.", result.height)
    return result


def get_siorg_organizations(power_code=None, sphere_code=None, use_cache=True,
                            verbose=False):
    """English alias for :func:`get_siorg_orgaos`."""
    return get_siorg_orgaos(codigo_poder=power_code, codigo_esfera=sphere_code,
                            use_cache=use_cache, verbose=verbose)


def get_siorg_estrutura(codigo_unidade, vinculados=None, use_cache=True,
                        verbose=False):
    """Get the organizational structure tree for a SIORG unit (flat DataFrame).

    Use the returned codes as ``organizacao_n2``/``organizacao_n3`` in CUSTOS.
    ``vinculados`` is ``"SIM"`` or ``"NAO"``.
    """
    check_required(codigo_unidade=codigo_unidade)
    params = {
        "codigoUnidade": codigo_unidade,
        "retornarOrgaoEntidadeVinculados": vinculados,
    }
    body = _siorg_fetch("/doc/estrutura-organizacional/resumida", params,
                        use_cache=use_cache, verbose=verbose)
    result = _parse_unidades(body)
    if result.height == 0:
        log.warning("No structure returned for unit %s.", codigo_unidade)
        return pl.DataFrame()
    log.info("Done: %s units in structure.", result.height)
    return result


def get_siorg_structure(unit_code, include_linked=None, use_cache=True,
                        verbose=False):
    """English alias for :func:`get_siorg_estrutura`."""
    check_required(unit_code=unit_code)
    return get_siorg_estrutura(codigo_unidade=unit_code,
                               vinculados=include_linked, use_cache=use_cache,
                               verbose=verbose)


def get_siorg_unidade(codigo_unidade, use_cache=True, verbose=False):
    """Get details of a single SIORG unit by its code (single-row DataFrame)."""
    check_required(codigo_unidade=codigo_unidade)
    path = f"/doc/unidade-organizacional/{codigo_unidade}/resumida"
    body = _siorg_fetch(path, use_cache=use_cache, verbose=verbose)

    unidade = body.get("unidade") if isinstance(body, Mapping) else None
    if not unidade:
        log.warning("No data returned for unit %s.", codigo_unidade)
        return pl.DataFrame()

    rec = {
        k: (None if v is None else str(v))
        for k, v in unidade.items()
        if v is not None
    }
    for col in _URI_COLS:
        if col in rec:
            rec[col] = _extract_siorg_code(rec[col])
    result = pl.from_dicts([rec], infer_schema_length=None)
    result = clean_names(result)
    log.info("Done: retrieved unit %s.", codigo_unidade)
    return result


def get_siorg_unit(unit_code, use_cache=True, verbose=False):
    """English alias for :func:`get_siorg_unidade`."""
    check_required(unit_code=unit_code)
    return get_siorg_unidade(codigo_unidade=unit_code, use_cache=use_cache,
                             verbose=verbose)
