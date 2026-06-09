"""SIOPE API functions (education spending data, FNDE/MEC).

API docs: https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/aplicacao
Base URL: https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata

Most endpoints share three required parameters: ``ano`` / ``year``,
``periodo`` / ``period`` (bimester 1-6) and ``uf`` / ``state``.
``get_siope_remuneracao`` additionally requires ``mes`` / ``month``.

All functions accept OData ``filter``, ``orderby`` and ``select`` to narrow
results server-side. Column names in those options must use the original API
names (uppercase), e.g. ``filter="NOM_MUNI eq 'Recife'"``.
"""

from __future__ import annotations

from ._core import INF, check_required, siope_fetch

__all__ = [
    "get_siope_dados_gerais", "get_siope_general_data",
    "get_siope_responsaveis", "get_siope_officials",
    "get_siope_despesas", "get_siope_expenses",
    "get_siope_despesas_funcao", "get_siope_expenses_by_function",
    "get_siope_indicadores", "get_siope_indicators",
    "get_siope_info_complementares", "get_siope_supplementary",
    "get_siope_receitas", "get_siope_revenues",
    "get_siope_remuneracao", "get_siope_compensation",
]


def _siope(resource, ano, periodo, uf, use_cache, verbose, page_size, max_rows,
           filter, orderby, select):
    check_required(ano=ano, periodo=periodo, uf=uf)
    params = {"Ano_Consulta": ano, "Num_Peri": periodo, "Sig_UF": uf}
    return siope_fetch(resource, params, use_cache=use_cache, verbose=verbose,
                       page_size=page_size, max_rows=max_rows, filter=filter,
                       orderby=orderby, select=select)


def get_siope_dados_gerais(ano, periodo, uf, use_cache=True, verbose=False,
                           page_size=1000, max_rows=INF, filter=None,
                           orderby=None, select=None):
    """Get SIOPE general data (demographics, GDP, revenues, expenses, metadata)."""
    return _siope("Dados_Gerais_Siope", ano, periodo, uf, use_cache, verbose,
                  page_size, max_rows, filter, orderby, select)


def get_siope_general_data(year, period, state, use_cache=True, verbose=False,
                           page_size=1000, max_rows=INF, filter=None,
                           orderby=None, select=None):
    """English alias for :func:`get_siope_dados_gerais`."""
    return get_siope_dados_gerais(ano=year, periodo=period, uf=state,
                                  use_cache=use_cache, verbose=verbose,
                                  page_size=page_size, max_rows=max_rows,
                                  filter=filter, orderby=orderby, select=select)


def get_siope_responsaveis(ano, periodo, uf, use_cache=True, verbose=False,
                           page_size=1000, max_rows=INF, filter=None,
                           orderby=None, select=None):
    """Get SIOPE officials/responsible persons data."""
    return _siope("Dados_Gerais_Siope_Dados_Responsaveis", ano, periodo, uf,
                  use_cache, verbose, page_size, max_rows, filter, orderby,
                  select)


def get_siope_officials(year, period, state, use_cache=True, verbose=False,
                        page_size=1000, max_rows=INF, filter=None, orderby=None,
                        select=None):
    """English alias for :func:`get_siope_responsaveis`."""
    return get_siope_responsaveis(ano=year, periodo=period, uf=state,
                                  use_cache=use_cache, verbose=verbose,
                                  page_size=page_size, max_rows=max_rows,
                                  filter=filter, orderby=orderby, select=select)


def get_siope_despesas(ano, periodo, uf, use_cache=True, verbose=False,
                       page_size=1000, max_rows=INF, filter=None, orderby=None,
                       select=None):
    """Get SIOPE education expenses data broken down by category."""
    return _siope("Despesas_Siope", ano, periodo, uf, use_cache, verbose,
                  page_size, max_rows, filter, orderby, select)


def get_siope_expenses(year, period, state, use_cache=True, verbose=False,
                       page_size=1000, max_rows=INF, filter=None, orderby=None,
                       select=None):
    """English alias for :func:`get_siope_despesas`."""
    return get_siope_despesas(ano=year, periodo=period, uf=state,
                              use_cache=use_cache, verbose=verbose,
                              page_size=page_size, max_rows=max_rows,
                              filter=filter, orderby=orderby, select=select)


def get_siope_despesas_funcao(ano, periodo, uf, use_cache=True, verbose=False,
                              page_size=1000, max_rows=INF, filter=None,
                              orderby=None, select=None):
    """Get SIOPE expenses broken down by government function."""
    return _siope("Despesas_Funcao_Educacao_Siope", ano, periodo, uf, use_cache,
                  verbose, page_size, max_rows, filter, orderby, select)


def get_siope_expenses_by_function(year, period, state, use_cache=True,
                                   verbose=False, page_size=1000, max_rows=INF,
                                   filter=None, orderby=None, select=None):
    """English alias for :func:`get_siope_despesas_funcao`."""
    return get_siope_despesas_funcao(ano=year, periodo=period, uf=state,
                                     use_cache=use_cache, verbose=verbose,
                                     page_size=page_size, max_rows=max_rows,
                                     filter=filter, orderby=orderby,
                                     select=select)


def get_siope_indicadores(ano, periodo, uf, use_cache=True, verbose=False,
                          page_size=1000, max_rows=INF, filter=None,
                          orderby=None, select=None):
    """Get SIOPE education indicators (e.g. % of revenue applied to education)."""
    return _siope("Indicadores_Siope", ano, periodo, uf, use_cache, verbose,
                  page_size, max_rows, filter, orderby, select)


def get_siope_indicators(year, period, state, use_cache=True, verbose=False,
                         page_size=1000, max_rows=INF, filter=None, orderby=None,
                         select=None):
    """English alias for :func:`get_siope_indicadores`."""
    return get_siope_indicadores(ano=year, periodo=period, uf=state,
                                 use_cache=use_cache, verbose=verbose,
                                 page_size=page_size, max_rows=max_rows,
                                 filter=filter, orderby=orderby, select=select)


def get_siope_info_complementares(ano, periodo, uf, use_cache=True,
                                  verbose=False, page_size=1000, max_rows=INF,
                                  filter=None, orderby=None, select=None):
    """Get SIOPE supplementary information from declarations."""
    return _siope("Informacoes_Complementares_Siope", ano, periodo, uf,
                  use_cache, verbose, page_size, max_rows, filter, orderby,
                  select)


def get_siope_supplementary(year, period, state, use_cache=True, verbose=False,
                            page_size=1000, max_rows=INF, filter=None,
                            orderby=None, select=None):
    """English alias for :func:`get_siope_info_complementares`."""
    return get_siope_info_complementares(ano=year, periodo=period, uf=state,
                                         use_cache=use_cache, verbose=verbose,
                                         page_size=page_size, max_rows=max_rows,
                                         filter=filter, orderby=orderby,
                                         select=select)


def get_siope_receitas(ano, periodo, uf, use_cache=True, verbose=False,
                       page_size=1000, max_rows=INF, filter=None, orderby=None,
                       select=None):
    """Get SIOPE education revenue data (tax revenues, transfers, FUNDEB)."""
    return _siope("Receita_Siope", ano, periodo, uf, use_cache, verbose,
                  page_size, max_rows, filter, orderby, select)


def get_siope_revenues(year, period, state, use_cache=True, verbose=False,
                       page_size=1000, max_rows=INF, filter=None, orderby=None,
                       select=None):
    """English alias for :func:`get_siope_receitas`."""
    return get_siope_receitas(ano=year, periodo=period, uf=state,
                              use_cache=use_cache, verbose=verbose,
                              page_size=page_size, max_rows=max_rows,
                              filter=filter, orderby=orderby, select=select)


def get_siope_remuneracao(ano, periodo, mes, uf, use_cache=True, verbose=False,
                          page_size=1000, max_rows=INF, filter=None,
                          orderby=None, select=None):
    """Get SIOPE staff compensation data. Requires an extra ``mes`` (month)."""
    check_required(ano=ano, periodo=periodo, mes=mes, uf=uf)
    params = {
        "Ano_Declaracao": ano,
        "Num_Peri": periodo,
        "Mes_Exercicio": mes,
        "Sig_UF": uf,
    }
    return siope_fetch("Remuneracao_Siope", params, use_cache=use_cache,
                       verbose=verbose, page_size=page_size, max_rows=max_rows,
                       filter=filter, orderby=orderby, select=select)


def get_siope_compensation(year, period, month, state, use_cache=True,
                           verbose=False, page_size=1000, max_rows=INF,
                           filter=None, orderby=None, select=None):
    """English alias for :func:`get_siope_remuneracao`."""
    return get_siope_remuneracao(ano=year, periodo=period, mes=month, uf=state,
                                 use_cache=use_cache, verbose=verbose,
                                 page_size=page_size, max_rows=max_rows,
                                 filter=filter, orderby=orderby, select=select)
