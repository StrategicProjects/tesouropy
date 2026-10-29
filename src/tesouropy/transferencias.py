"""Transferencias Constitucionais API functions.

Docs: https://apiapex.tesouro.gov.br/aria/v1/transferencias_constitucionais/docs

IMPORTANT: all filter parameters use NUMERIC CODES from the Treasury's internal
systems. These are NOT IBGE codes. Use the dictionary functions to look codes
up: :func:`get_tc_transferencias`, :func:`get_tc_estados`,
:func:`get_tc_municipios`.

Multi-value parameters accept either a colon-separated string (``"1:2:3"``) or
a Python sequence (``[1, 2, 3]``).
"""

from __future__ import annotations

from ._core import (
    INF,
    check_not_uf_abbrev,
    collapse_param,
    transferencias_fetch,
    transferencias_fetch_all,
)

__all__ = [
    "get_tc_transferencias", "get_tc_transfer_types",
    "get_tc_estados", "get_tc_states",
    "get_tc_municipios", "get_tc_municipalities",
    "get_tc_por_estados", "get_tc_by_state",
    "get_tc_por_estados_detalhe", "get_tc_by_state_detail",
    "get_tc_por_municipio", "get_tc_by_municipality",
    "get_tc_por_municipio_detalhe", "get_tc_by_municipality_detail",
]


# -- Dictionaries -------------------------------------------------------------


def get_tc_transferencias(use_cache=True, verbose=False):
    """Get the transfer-type dictionary (``codigo``, ``nome``).

    These are internal Treasury codes, not IBGE codes.
    """
    return transferencias_fetch("/transferencias", use_cache=use_cache,
                                verbose=verbose)


def get_tc_transfer_types(use_cache=True, verbose=False):
    """English alias for :func:`get_tc_transferencias`."""
    return get_tc_transferencias(use_cache=use_cache, verbose=verbose)


def get_tc_estados(use_cache=True, verbose=False):
    """Get the state dictionary (``codigo``, ``nome``).

    These are internal Treasury codes, not IBGE codes.
    """
    return transferencias_fetch("/estados", use_cache=use_cache, verbose=verbose)


def get_tc_states(use_cache=True, verbose=False):
    """English alias for :func:`get_tc_estados`."""
    return get_tc_estados(use_cache=use_cache, verbose=verbose)


def get_tc_municipios(p_nome=None, p_uf=None, use_cache=True, verbose=False):
    """Get the municipality dictionary.

    ``p_uf`` is a Treasury state code from :func:`get_tc_estados` (not a UF
    abbreviation or IBGE code).
    """
    check_not_uf_abbrev(p_uf, "p_uf")
    params = {"p_nome": p_nome, "p_uf": p_uf}
    return transferencias_fetch("/municipios", params, use_cache=use_cache,
                                verbose=verbose)


def get_tc_municipalities(name=None, state_code=None, use_cache=True,
                          verbose=False):
    """English alias for :func:`get_tc_municipios`."""
    return get_tc_municipios(p_nome=name, p_uf=state_code, use_cache=use_cache,
                             verbose=verbose)


# -- By state -----------------------------------------------------------------


def get_tc_por_estados(p_estado=None, p_ano=None, p_mes=None,
                       p_transferencia=None, p_sn_detalhar=None, use_cache=True,
                       verbose=False):
    """Get constitutional transfers aggregated by state.

    Multi-value parameters accept a sequence or a colon-separated string.
    """
    check_not_uf_abbrev(p_estado, "p_estado")
    params = {
        "p_estado": collapse_param(p_estado),
        "p_ano": collapse_param(p_ano),
        "p_mes": collapse_param(p_mes),
        "p_transferencia": collapse_param(p_transferencia),
        "p_sn_detalhar": p_sn_detalhar,
    }
    return transferencias_fetch("/por_estados", params, use_cache=use_cache,
                                verbose=verbose)


def get_tc_by_state(state_code=None, year=None, month=None, transfer_type=None,
                    detailed=None, use_cache=True, verbose=False):
    """English alias for :func:`get_tc_por_estados`."""
    return get_tc_por_estados(p_estado=state_code, p_ano=year, p_mes=month,
                              p_transferencia=transfer_type,
                              p_sn_detalhar=detailed, use_cache=use_cache,
                              verbose=verbose)


def get_tc_por_estados_detalhe(p_estado=None, p_ano=None, p_mes=None,
                               p_transferencia=None, use_cache=True,
                               verbose=False):
    """Get detailed constitutional transfers by state."""
    check_not_uf_abbrev(p_estado, "p_estado")
    params = {
        "p_estado": collapse_param(p_estado),
        "p_ano": collapse_param(p_ano),
        "p_mes": collapse_param(p_mes),
        "p_transferencia": collapse_param(p_transferencia),
    }
    return transferencias_fetch("/por_estados_detalhe", params,
                                use_cache=use_cache, verbose=verbose)


def get_tc_by_state_detail(state_code=None, year=None, month=None,
                           transfer_type=None, use_cache=True, verbose=False):
    """English alias for :func:`get_tc_por_estados_detalhe`."""
    return get_tc_por_estados_detalhe(p_estado=state_code, p_ano=year,
                                      p_mes=month,
                                      p_transferencia=transfer_type,
                                      use_cache=use_cache, verbose=verbose)


# -- By municipality ----------------------------------------------------------


def get_tc_por_municipio(p_estado=None, p_municipio=None, p_ano=None, p_mes=None,
                         p_transferencia=None, p_sn_detalhar=None, use_cache=True,
                         verbose=False, page_size=1000, max_rows=INF):
    """Get constitutional transfers for municipalities within states.

    The server-side contract changed in 2026-09: parameter names are
    case-sensitive lower case (``p_municipio`` in the singular) and the
    response is paginated (10 rows per page by default upstream). With the
    old upper-case names the server ignored every filter and timed out
    (HTTP 504), so this function fetches every page with the names the
    server expects. If a page after the first fails, the rows already
    fetched are returned with ``result.partial == True``.
    """
    check_not_uf_abbrev(p_estado, "p_estado")
    params = {
        "p_estado": collapse_param(p_estado),
        "p_municipio": collapse_param(p_municipio),
        "p_ano": collapse_param(p_ano),
        "p_mes": collapse_param(p_mes),
        "p_transferencia": collapse_param(p_transferencia),
        "p_sn_detalhar": p_sn_detalhar,
    }
    return transferencias_fetch_all("/por_estado_municipio", params,
                                    page_size=page_size, max_rows=max_rows,
                                    use_cache=use_cache, verbose=verbose)


def get_tc_by_municipality(state_code=None, municipality=None, year=None,
                           month=None, transfer_type=None, detailed=None,
                           use_cache=True, verbose=False, page_size=1000,
                           max_rows=INF):
    """English alias for :func:`get_tc_por_municipio`."""
    return get_tc_por_municipio(p_estado=state_code, p_municipio=municipality,
                                p_ano=year, p_mes=month,
                                p_transferencia=transfer_type,
                                p_sn_detalhar=detailed, use_cache=use_cache,
                                verbose=verbose, page_size=page_size,
                                max_rows=max_rows)


def get_tc_por_municipio_detalhe(p_estado=None, p_municipio=None, p_ano=None,
                                 p_mes=None, p_transferencia=None, use_cache=True,
                                 verbose=False):
    """Get detailed constitutional transfers by municipality.

    Unlike ``/por_estado_municipio``, this endpoint kept its original
    contract: UPPERCASE parameter names, ``P_MUNICIPIOS`` in the plural and
    no pagination (lower-case names answer HTTP 504). It returns the three
    ten-day installments (``va_primeiro_dec``, ``va_segundo_dec``,
    ``va_terceiro_dec``) plus ``total``.
    """
    check_not_uf_abbrev(p_estado, "p_estado")
    params = {
        "P_ESTADO": collapse_param(p_estado),
        "P_MUNICIPIOS": collapse_param(p_municipio),
        "P_ANO": collapse_param(p_ano),
        "P_MES": collapse_param(p_mes),
        "P_TRANSFERENCIA": collapse_param(p_transferencia),
    }
    return transferencias_fetch("/por_estado_municipio_detalhe", params,
                                use_cache=use_cache, verbose=verbose)


def get_tc_by_municipality_detail(state_code=None, municipality=None, year=None,
                                  month=None, transfer_type=None, use_cache=True,
                                  verbose=False):
    """English alias for :func:`get_tc_por_municipio_detalhe`."""
    return get_tc_por_municipio_detalhe(p_estado=state_code,
                                        p_municipio=municipality, p_ano=year,
                                        p_mes=month,
                                        p_transferencia=transfer_type,
                                        use_cache=use_cache, verbose=verbose)
