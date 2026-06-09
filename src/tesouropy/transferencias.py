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

from ._core import check_not_uf_abbrev, collapse_param, transferencias_fetch

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
                         verbose=False):
    """Get constitutional transfers for municipalities within states.

    Note: this endpoint expects UPPERCASE parameter names upstream; the
    conversion is handled internally.
    """
    check_not_uf_abbrev(p_estado, "p_estado")
    params = {
        "P_ESTADO": collapse_param(p_estado),
        "P_MUNICIPIOS": collapse_param(p_municipio),
        "P_ANO": collapse_param(p_ano),
        "P_MES": collapse_param(p_mes),
        "P_TRANSFERENCIA": collapse_param(p_transferencia),
        "P_SN_DETALHAR": p_sn_detalhar,
    }
    return transferencias_fetch("/por_estado_municipio", params,
                                use_cache=use_cache, verbose=verbose)


def get_tc_by_municipality(state_code=None, municipality=None, year=None,
                           month=None, transfer_type=None, detailed=None,
                           use_cache=True, verbose=False):
    """English alias for :func:`get_tc_por_municipio`."""
    return get_tc_por_municipio(p_estado=state_code, p_municipio=municipality,
                                p_ano=year, p_mes=month,
                                p_transferencia=transfer_type,
                                p_sn_detalhar=detailed, use_cache=use_cache,
                                verbose=verbose)


def get_tc_por_municipio_detalhe(p_estado=None, p_municipio=None, p_ano=None,
                                 p_mes=None, p_transferencia=None, use_cache=True,
                                 verbose=False):
    """Get detailed constitutional transfers by municipality."""
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
