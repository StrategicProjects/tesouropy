"""CUSTOS API functions (federal government cost data).

API docs: https://apidatalake.tesouro.gov.br/docs/custos/

PERFORMANCE WARNING: the CUSTOS API is slow (server default 250 rows/page,
frequent HTTP 504 timeouts). Unfiltered queries return hundreds of thousands of
rows. Always filter by ``organizacao_n1`` + ``organizacao_n2``, ``ano`` +
``mes``, ``natureza_juridica``, and/or cap with ``max_rows``.

SIORG codes are auto-padded: pass ``244`` or ``"244"``; both become ``"000244"``.
Use :func:`tesouropy.get_siorg_orgaos` / :func:`tesouropy.get_siorg_estrutura`
to look up codes.
"""

from __future__ import annotations

from ._core import INF, custos_fetch_all, pad_siorg_code

__all__ = [
    "get_custos_pessoal_ativo", "get_costs_active_staff",
    "get_custos_pessoal_inativo", "get_costs_retired_staff",
    "get_custos_pensionistas", "get_costs_pensioners",
    "get_custos_demais", "get_costs_other",
    "get_custos_depreciacao", "get_costs_depreciation",
    "get_custos_transferencias", "get_costs_transfers",
]


def _custos_params(ano, mes, natureza_juridica, organizacao_n1, organizacao_n2,
                   organizacao_n3):
    return {
        "ano": ano,
        "mes": mes,
        "natureza_juridica": natureza_juridica,
        "organizacao_n1": pad_siorg_code(organizacao_n1),
        "organizacao_n2": pad_siorg_code(organizacao_n2),
        "organizacao_n3": pad_siorg_code(organizacao_n3),
    }


def _custos(endpoint, ano, mes, natureza_juridica, organizacao_n1,
            organizacao_n2, organizacao_n3, use_cache, verbose, page_size,
            max_rows):
    params = _custos_params(ano, mes, natureza_juridica, organizacao_n1,
                            organizacao_n2, organizacao_n3)
    return custos_fetch_all(endpoint, params, use_cache=use_cache,
                            verbose=verbose, page_size=page_size,
                            max_rows=max_rows)


def get_custos_pessoal_ativo(ano=None, mes=None, natureza_juridica=None,
                             organizacao_n1=None, organizacao_n2=None,
                             organizacao_n3=None, use_cache=True, verbose=False,
                             page_size=500, max_rows=INF):
    """Get active staff cost data. All parameters are optional filters.

    ``natureza_juridica``: ``1`` Public Company, ``2`` Public Foundation,
    ``3`` Direct Administration, ``4`` Autarchy, ``6`` Mixed Economy Company.
    ``organizacao_n*`` are SIORG codes (auto zero-padded to 6 digits).
    """
    return _custos("/pessoal_ativo", ano, mes, natureza_juridica,
                   organizacao_n1, organizacao_n2, organizacao_n3, use_cache,
                   verbose, page_size, max_rows)


def get_costs_active_staff(year=None, month=None, legal_nature=None,
                           org_level1=None, org_level2=None, org_level3=None,
                           use_cache=True, verbose=False, page_size=500,
                           max_rows=INF):
    """English alias for :func:`get_custos_pessoal_ativo`."""
    return get_custos_pessoal_ativo(ano=year, mes=month,
                                    natureza_juridica=legal_nature,
                                    organizacao_n1=org_level1,
                                    organizacao_n2=org_level2,
                                    organizacao_n3=org_level3,
                                    use_cache=use_cache, verbose=verbose,
                                    page_size=page_size, max_rows=max_rows)


def get_custos_pessoal_inativo(ano=None, mes=None, natureza_juridica=None,
                               organizacao_n1=None, organizacao_n2=None,
                               organizacao_n3=None, use_cache=True,
                               verbose=False, page_size=500, max_rows=INF):
    """Get retired (inactive) staff cost data. All parameters are optional."""
    return _custos("/pessoal_inativo", ano, mes, natureza_juridica,
                   organizacao_n1, organizacao_n2, organizacao_n3, use_cache,
                   verbose, page_size, max_rows)


def get_costs_retired_staff(year=None, month=None, legal_nature=None,
                            org_level1=None, org_level2=None, org_level3=None,
                            use_cache=True, verbose=False, page_size=500,
                            max_rows=INF):
    """English alias for :func:`get_custos_pessoal_inativo`."""
    return get_custos_pessoal_inativo(ano=year, mes=month,
                                      natureza_juridica=legal_nature,
                                      organizacao_n1=org_level1,
                                      organizacao_n2=org_level2,
                                      organizacao_n3=org_level3,
                                      use_cache=use_cache, verbose=verbose,
                                      page_size=page_size, max_rows=max_rows)


def get_custos_pensionistas(ano=None, mes=None, natureza_juridica=None,
                            organizacao_n1=None, organizacao_n2=None,
                            organizacao_n3=None, use_cache=True, verbose=False,
                            page_size=500, max_rows=INF):
    """Get pensioner cost data. All parameters are optional filters."""
    return _custos("/pensionistas", ano, mes, natureza_juridica, organizacao_n1,
                   organizacao_n2, organizacao_n3, use_cache, verbose,
                   page_size, max_rows)


def get_costs_pensioners(year=None, month=None, legal_nature=None,
                         org_level1=None, org_level2=None, org_level3=None,
                         use_cache=True, verbose=False, page_size=500,
                         max_rows=INF):
    """English alias for :func:`get_custos_pensionistas`."""
    return get_custos_pensionistas(ano=year, mes=month,
                                   natureza_juridica=legal_nature,
                                   organizacao_n1=org_level1,
                                   organizacao_n2=org_level2,
                                   organizacao_n3=org_level3,
                                   use_cache=use_cache, verbose=verbose,
                                   page_size=page_size, max_rows=max_rows)


def get_custos_demais(ano=None, mes=None, natureza_juridica=None,
                      organizacao_n1=None, organizacao_n2=None,
                      organizacao_n3=None, use_cache=True, verbose=False,
                      page_size=500, max_rows=INF):
    """Get other (non-personnel) cost data. All parameters are optional."""
    return _custos("/demais", ano, mes, natureza_juridica, organizacao_n1,
                   organizacao_n2, organizacao_n3, use_cache, verbose,
                   page_size, max_rows)


def get_costs_other(year=None, month=None, legal_nature=None, org_level1=None,
                    org_level2=None, org_level3=None, use_cache=True,
                    verbose=False, page_size=500, max_rows=INF):
    """English alias for :func:`get_custos_demais`."""
    return get_custos_demais(ano=year, mes=month, natureza_juridica=legal_nature,
                             organizacao_n1=org_level1, organizacao_n2=org_level2,
                             organizacao_n3=org_level3, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_custos_depreciacao(ano=None, mes=None, natureza_juridica=None,
                           organizacao_n1=None, organizacao_n2=None,
                           organizacao_n3=None, use_cache=True, verbose=False,
                           page_size=500, max_rows=INF):
    """Get depreciation cost data. All parameters are optional filters."""
    return _custos("/depreciacao", ano, mes, natureza_juridica, organizacao_n1,
                   organizacao_n2, organizacao_n3, use_cache, verbose,
                   page_size, max_rows)


def get_costs_depreciation(year=None, month=None, legal_nature=None,
                           org_level1=None, org_level2=None, org_level3=None,
                           use_cache=True, verbose=False, page_size=500,
                           max_rows=INF):
    """English alias for :func:`get_custos_depreciacao`."""
    return get_custos_depreciacao(ano=year, mes=month,
                                  natureza_juridica=legal_nature,
                                  organizacao_n1=org_level1,
                                  organizacao_n2=org_level2,
                                  organizacao_n3=org_level3, use_cache=use_cache,
                                  verbose=verbose, page_size=page_size,
                                  max_rows=max_rows)


def get_custos_transferencias(ano=None, mes=None, natureza_juridica=None,
                              organizacao_n1=None, organizacao_n2=None,
                              organizacao_n3=None, use_cache=True, verbose=False,
                              page_size=500, max_rows=INF):
    """Get transfer cost data. All parameters are optional filters."""
    return _custos("/transferencias", ano, mes, natureza_juridica,
                   organizacao_n1, organizacao_n2, organizacao_n3, use_cache,
                   verbose, page_size, max_rows)


def get_costs_transfers(year=None, month=None, legal_nature=None,
                        org_level1=None, org_level2=None, org_level3=None,
                        use_cache=True, verbose=False, page_size=500,
                        max_rows=INF):
    """English alias for :func:`get_custos_transferencias`."""
    return get_custos_transferencias(ano=year, mes=month,
                                     natureza_juridica=legal_nature,
                                     organizacao_n1=org_level1,
                                     organizacao_n2=org_level2,
                                     organizacao_n3=org_level3,
                                     use_cache=use_cache, verbose=verbose,
                                     page_size=page_size, max_rows=max_rows)
