"""SICONFI API functions (RREO, RGF, DCA, MSC, entities).

API docs: https://apidatalake.tesouro.gov.br/docs/siconfi/

Every public function has a Portuguese name (PT parameters) and an English
alias that maps the English parameter names onto the PT ones.
"""

from __future__ import annotations

from ._core import (
    INF,
    check_required,
    resolve_state_munis,
    siconfi_fetch_all,
    tnr_loop,
)

__all__ = [
    "get_entes", "get_entities",
    "get_anexos", "get_annexes",
    "get_dca", "get_annual_accounts",
    "get_dca_for_state", "get_annual_accounts_for_state",
    "get_extrato", "get_delivery_status",
    "get_rreo", "get_budget_report",
    "get_rreo_for_state", "get_budget_report_for_state",
    "get_rgf", "get_fiscal_report",
    "get_rgf_for_state", "get_fiscal_report_for_state",
    "get_msc_controle", "get_msc_control",
    "get_msc_orcamentaria", "get_msc_budget",
    "get_msc_patrimonial", "get_msc_equity",
]


# -- get_entes / get_entities -------------------------------------------------


def get_entes(use_cache=True, verbose=False, page_size=None, max_rows=INF):
    """Get the list of Brazilian government entities (states, municipalities, DF).

    Returns a polars DataFrame with columns ``cod_ibge``, ``ente``, ``capital``,
    ``regiao``, ``uf``, ``esfera``, ``an_exercicio``, ``populacao``, ``co_cnpj``.
    """
    return siconfi_fetch_all(
        "/entes", use_cache=use_cache, verbose=verbose, page_size=page_size,
        max_rows=max_rows,
    )


def get_entities(use_cache=True, verbose=False, page_size=None, max_rows=INF):
    """English alias for :func:`get_entes`."""
    return get_entes(use_cache=use_cache, verbose=verbose, page_size=page_size,
                     max_rows=max_rows)


# -- get_anexos / get_annexes -------------------------------------------------


def get_anexos(use_cache=True, verbose=False, page_size=None, max_rows=INF):
    """Get the report appendix reference table grouped by government sphere."""
    return siconfi_fetch_all(
        "/anexos-relatorios", use_cache=use_cache, verbose=verbose,
        page_size=page_size, max_rows=max_rows,
    )


def get_annexes(use_cache=True, verbose=False, page_size=None, max_rows=INF):
    """English alias for :func:`get_anexos`."""
    return get_anexos(use_cache=use_cache, verbose=verbose, page_size=page_size,
                      max_rows=max_rows)


# -- get_dca / get_annual_accounts --------------------------------------------


def get_dca(an_exercicio, id_ente, no_anexo=None, use_cache=True, verbose=False,
            page_size=None, max_rows=INF):
    """Get Annual Accounts Declaration (DCA) data for an entity and fiscal year.

    Parameters
    ----------
    an_exercicio : int
        Fiscal year (e.g. ``2022``). Required.
    id_ente : int
        IBGE code of the entity. Required.
    no_anexo : str, optional
        Appendix name filter (e.g. ``"DCA-Anexo I-AB"``).
    """
    check_required(an_exercicio=an_exercicio, id_ente=id_ente)
    params = {
        "an_exercicio": an_exercicio,
        "id_ente": id_ente,
        "no_anexo": no_anexo,
    }
    return siconfi_fetch_all("/dca", params, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_annual_accounts(fiscal_year, entity_id, appendix=None, use_cache=True,
                        verbose=False, page_size=None, max_rows=INF):
    """English alias for :func:`get_dca`."""
    check_required(fiscal_year=fiscal_year, entity_id=entity_id)
    return get_dca(an_exercicio=fiscal_year, id_ente=entity_id,
                   no_anexo=appendix, use_cache=use_cache, verbose=verbose,
                   page_size=page_size, max_rows=max_rows)


# -- get_dca_for_state / get_annual_accounts_for_state ------------------------


def get_dca_for_state(state_uf, an_exercicio, no_anexo=None,
                      include_capital=True, on_error="warn", use_cache=True,
                      verbose=False, page_size=None, max_rows=INF):
    """Get DCA data for every municipality of a Brazilian state (fault tolerant).

    Failed calls are recorded on ``result.failed``.
    """
    check_required(state_uf=state_uf, an_exercicio=an_exercicio)
    munis = resolve_state_munis(state_uf, include_capital=include_capital,
                                use_cache=use_cache, verbose=verbose)
    param_list = [
        {
            "an_exercicio": an_exercicio,
            "id_ente": id_ente,
            "no_anexo": no_anexo,
            "use_cache": use_cache,
            "verbose": verbose,
            "page_size": page_size,
            "max_rows": max_rows,
        }
        for id_ente in munis["cod_ibge"].to_list()
    ]
    return tnr_loop(get_dca, param_list, id_key="id_ente", on_error=on_error,
                    progress_label=f"DCA {state_uf}")


def get_annual_accounts_for_state(state_uf, fiscal_year, appendix=None,
                                  include_capital=True, on_error="warn",
                                  use_cache=True, verbose=False, page_size=None,
                                  max_rows=INF):
    """English alias for :func:`get_dca_for_state`."""
    check_required(state_uf=state_uf, fiscal_year=fiscal_year)
    return get_dca_for_state(state_uf=state_uf, an_exercicio=fiscal_year,
                             no_anexo=appendix, include_capital=include_capital,
                             on_error=on_error, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


# -- get_extrato / get_delivery_status ----------------------------------------


def get_extrato(id_ente, an_referencia, use_cache=True, verbose=False,
                page_size=None, max_rows=INF):
    """Get the delivery status extract for an entity and reference year."""
    check_required(id_ente=id_ente, an_referencia=an_referencia)
    params = {"id_ente": id_ente, "an_referencia": an_referencia}
    return siconfi_fetch_all("/extrato_entregas", params, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_delivery_status(entity_id, year, use_cache=True, verbose=False,
                        page_size=None, max_rows=INF):
    """English alias for :func:`get_extrato`."""
    check_required(entity_id=entity_id, year=year)
    return get_extrato(id_ente=entity_id, an_referencia=year,
                       use_cache=use_cache, verbose=verbose, page_size=page_size,
                       max_rows=max_rows)


# -- get_rreo / get_budget_report ---------------------------------------------


def get_rreo(an_exercicio, nr_periodo, co_tipo_demonstrativo, no_anexo, id_ente,
             co_esfera=None, use_cache=True, verbose=False, page_size=None,
             max_rows=INF):
    """Get Budget Execution Summary Report (RREO) data.

    ``co_esfera`` is optional: some entities (e.g. the Federal District
    constitutional fund) only return data when the sphere filter is omitted, so
    leave it ``None`` if a sphere-filtered call comes back empty.
    """
    check_required(an_exercicio=an_exercicio, nr_periodo=nr_periodo,
                   co_tipo_demonstrativo=co_tipo_demonstrativo,
                   no_anexo=no_anexo, id_ente=id_ente)
    params = {
        "an_exercicio": an_exercicio,
        "nr_periodo": nr_periodo,
        "co_tipo_demonstrativo": co_tipo_demonstrativo,
        "no_anexo": no_anexo,
        "co_esfera": co_esfera,
        "id_ente": id_ente,
    }
    return siconfi_fetch_all("/rreo", params, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_budget_report(fiscal_year, period, report_type, appendix, entity_id,
                      sphere=None, use_cache=True, verbose=False, page_size=None,
                      max_rows=INF):
    """English alias for :func:`get_rreo`."""
    check_required(fiscal_year=fiscal_year, period=period,
                   report_type=report_type, appendix=appendix,
                   entity_id=entity_id)
    return get_rreo(an_exercicio=fiscal_year, nr_periodo=period,
                    co_tipo_demonstrativo=report_type, no_anexo=appendix,
                    id_ente=entity_id, co_esfera=sphere, use_cache=use_cache,
                    verbose=verbose, page_size=page_size, max_rows=max_rows)


# -- get_rreo_for_state / get_budget_report_for_state -------------------------


def get_rreo_for_state(state_uf, an_exercicio, nr_periodo,
                       co_tipo_demonstrativo, no_anexo, include_capital=True,
                       on_error="warn", use_cache=True, verbose=False,
                       page_size=None, max_rows=INF):
    """Get RREO data for every municipality of a Brazilian state (fault tolerant).

    Failed calls are recorded on ``result.failed``.
    """
    check_required(state_uf=state_uf, an_exercicio=an_exercicio,
                   nr_periodo=nr_periodo,
                   co_tipo_demonstrativo=co_tipo_demonstrativo,
                   no_anexo=no_anexo)
    munis = resolve_state_munis(state_uf, include_capital=include_capital,
                                use_cache=use_cache, verbose=verbose)
    param_list = [
        {
            "an_exercicio": an_exercicio,
            "nr_periodo": nr_periodo,
            "co_tipo_demonstrativo": co_tipo_demonstrativo,
            "no_anexo": no_anexo,
            "co_esfera": "M",
            "id_ente": id_ente,
            "use_cache": use_cache,
            "verbose": verbose,
            "page_size": page_size,
            "max_rows": max_rows,
        }
        for id_ente in munis["cod_ibge"].to_list()
    ]
    return tnr_loop(get_rreo, param_list, id_key="id_ente", on_error=on_error,
                    progress_label=f"RREO {state_uf}")


def get_budget_report_for_state(state_uf, fiscal_year, period, report_type,
                                appendix, include_capital=True, on_error="warn",
                                use_cache=True, verbose=False, page_size=None,
                                max_rows=INF):
    """English alias for :func:`get_rreo_for_state`."""
    check_required(state_uf=state_uf, fiscal_year=fiscal_year, period=period,
                   report_type=report_type, appendix=appendix)
    return get_rreo_for_state(state_uf=state_uf, an_exercicio=fiscal_year,
                              nr_periodo=period,
                              co_tipo_demonstrativo=report_type,
                              no_anexo=appendix,
                              include_capital=include_capital, on_error=on_error,
                              use_cache=use_cache, verbose=verbose,
                              page_size=page_size, max_rows=max_rows)


# -- get_rgf / get_fiscal_report ----------------------------------------------


def get_rgf(an_exercicio, in_periodicidade, nr_periodo, co_tipo_demonstrativo,
            no_anexo, co_esfera, co_poder, id_ente, use_cache=True,
            verbose=False, page_size=None, max_rows=INF):
    """Get Fiscal Management Report (RGF) data.

    ``in_periodicidade`` is ``"Q"`` (four-monthly) or ``"S"`` (semi-annual);
    ``co_poder`` is the branch: ``"E"`` exec, ``"L"`` legislative, ``"J"``
    judiciary, ``"M"`` public ministry, ``"D"`` public defender.
    """
    check_required(an_exercicio=an_exercicio, in_periodicidade=in_periodicidade,
                   nr_periodo=nr_periodo,
                   co_tipo_demonstrativo=co_tipo_demonstrativo,
                   no_anexo=no_anexo, co_esfera=co_esfera, co_poder=co_poder,
                   id_ente=id_ente)
    params = {
        "an_exercicio": an_exercicio,
        "in_periodicidade": in_periodicidade,
        "nr_periodo": nr_periodo,
        "co_tipo_demonstrativo": co_tipo_demonstrativo,
        "no_anexo": no_anexo,
        "co_esfera": co_esfera,
        "co_poder": co_poder,
        "id_ente": id_ente,
    }
    return siconfi_fetch_all("/rgf", params, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_fiscal_report(fiscal_year, periodicity, period, report_type, appendix,
                      sphere, branch, entity_id, use_cache=True, verbose=False,
                      page_size=None, max_rows=INF):
    """English alias for :func:`get_rgf`."""
    check_required(fiscal_year=fiscal_year, periodicity=periodicity,
                   period=period, report_type=report_type, appendix=appendix,
                   sphere=sphere, branch=branch, entity_id=entity_id)
    return get_rgf(an_exercicio=fiscal_year, in_periodicidade=periodicity,
                   nr_periodo=period, co_tipo_demonstrativo=report_type,
                   no_anexo=appendix, co_esfera=sphere, co_poder=branch,
                   id_ente=entity_id, use_cache=use_cache, verbose=verbose,
                   page_size=page_size, max_rows=max_rows)


# -- get_rgf_for_state / get_fiscal_report_for_state --------------------------


def get_rgf_for_state(state_uf, an_exercicio, in_periodicidade, nr_periodo,
                      co_tipo_demonstrativo, no_anexo, co_poder,
                      include_capital=True, on_error="warn", use_cache=True,
                      verbose=False, page_size=None, max_rows=INF):
    """Get RGF data for every municipality of a Brazilian state (fault tolerant)."""
    check_required(state_uf=state_uf, an_exercicio=an_exercicio,
                   in_periodicidade=in_periodicidade, nr_periodo=nr_periodo,
                   co_tipo_demonstrativo=co_tipo_demonstrativo,
                   no_anexo=no_anexo, co_poder=co_poder)
    munis = resolve_state_munis(state_uf, include_capital=include_capital,
                                use_cache=use_cache, verbose=verbose)
    param_list = [
        {
            "an_exercicio": an_exercicio,
            "in_periodicidade": in_periodicidade,
            "nr_periodo": nr_periodo,
            "co_tipo_demonstrativo": co_tipo_demonstrativo,
            "no_anexo": no_anexo,
            "co_esfera": "M",
            "co_poder": co_poder,
            "id_ente": id_ente,
            "use_cache": use_cache,
            "verbose": verbose,
            "page_size": page_size,
            "max_rows": max_rows,
        }
        for id_ente in munis["cod_ibge"].to_list()
    ]
    return tnr_loop(get_rgf, param_list, id_key="id_ente", on_error=on_error,
                    progress_label=f"RGF {state_uf}")


def get_fiscal_report_for_state(state_uf, fiscal_year, periodicity, period,
                                report_type, appendix, branch,
                                include_capital=True, on_error="warn",
                                use_cache=True, verbose=False, page_size=None,
                                max_rows=INF):
    """English alias for :func:`get_rgf_for_state`."""
    check_required(state_uf=state_uf, fiscal_year=fiscal_year,
                   periodicity=periodicity, period=period,
                   report_type=report_type, appendix=appendix, branch=branch)
    return get_rgf_for_state(state_uf=state_uf, an_exercicio=fiscal_year,
                             in_periodicidade=periodicity, nr_periodo=period,
                             co_tipo_demonstrativo=report_type,
                             no_anexo=appendix, co_poder=branch,
                             include_capital=include_capital, on_error=on_error,
                             use_cache=use_cache, verbose=verbose,
                             page_size=page_size, max_rows=max_rows)


# -- MSC: control / budget / equity -------------------------------------------


def _get_msc(endpoint, id_ente, an_referencia, me_referencia, co_tipo_matriz,
             classe_conta, id_tv, use_cache, verbose, page_size, max_rows):
    check_required(id_ente=id_ente, an_referencia=an_referencia,
                   me_referencia=me_referencia, co_tipo_matriz=co_tipo_matriz,
                   classe_conta=classe_conta, id_tv=id_tv)
    params = {
        "id_ente": id_ente,
        "an_referencia": an_referencia,
        "me_referencia": me_referencia,
        "co_tipo_matriz": co_tipo_matriz,
        "classe_conta": classe_conta,
        "id_tv": id_tv,
    }
    return siconfi_fetch_all(endpoint, params, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_msc_controle(id_ente, an_referencia, me_referencia, co_tipo_matriz,
                     classe_conta, id_tv, use_cache=True, verbose=False,
                     page_size=None, max_rows=INF):
    """Get MSC control accounts data (classes 7 and 8).

    ``co_tipo_matriz`` is ``"MSCC"`` (monthly aggregate) or ``"MSCE"`` (annual
    closing); ``id_tv`` is ``"beginning_balance"``, ``"ending_balance"`` or
    ``"period_change"``.
    """
    return _get_msc("/msc_controle", id_ente, an_referencia, me_referencia,
                    co_tipo_matriz, classe_conta, id_tv, use_cache, verbose,
                    page_size, max_rows)


def get_msc_control(entity_id, year, month, matrix_type, account_class,
                    value_type, use_cache=True, verbose=False, page_size=None,
                    max_rows=INF):
    """English alias for :func:`get_msc_controle`."""
    return get_msc_controle(id_ente=entity_id, an_referencia=year,
                            me_referencia=month, co_tipo_matriz=matrix_type,
                            classe_conta=account_class, id_tv=value_type,
                            use_cache=use_cache, verbose=verbose,
                            page_size=page_size, max_rows=max_rows)


def get_msc_orcamentaria(id_ente, an_referencia, me_referencia, co_tipo_matriz,
                         classe_conta, id_tv, use_cache=True, verbose=False,
                         page_size=None, max_rows=INF):
    """Get MSC budgetary accounts data (classes 5 and 6)."""
    return _get_msc("/msc_orcamentaria", id_ente, an_referencia, me_referencia,
                    co_tipo_matriz, classe_conta, id_tv, use_cache, verbose,
                    page_size, max_rows)


def get_msc_budget(entity_id, year, month, matrix_type, account_class,
                   value_type, use_cache=True, verbose=False, page_size=None,
                   max_rows=INF):
    """English alias for :func:`get_msc_orcamentaria`."""
    return get_msc_orcamentaria(id_ente=entity_id, an_referencia=year,
                                me_referencia=month, co_tipo_matriz=matrix_type,
                                classe_conta=account_class, id_tv=value_type,
                                use_cache=use_cache, verbose=verbose,
                                page_size=page_size, max_rows=max_rows)


def get_msc_patrimonial(id_ente, an_referencia, me_referencia, co_tipo_matriz,
                        classe_conta, id_tv, use_cache=True, verbose=False,
                        page_size=None, max_rows=INF):
    """Get MSC equity/asset accounts data (classes 1 to 4)."""
    return _get_msc("/msc_patrimonial", id_ente, an_referencia, me_referencia,
                    co_tipo_matriz, classe_conta, id_tv, use_cache, verbose,
                    page_size, max_rows)


def get_msc_equity(entity_id, year, month, matrix_type, account_class,
                   value_type, use_cache=True, verbose=False, page_size=None,
                   max_rows=INF):
    """English alias for :func:`get_msc_patrimonial`."""
    return get_msc_patrimonial(id_ente=entity_id, an_referencia=year,
                               me_referencia=month, co_tipo_matriz=matrix_type,
                               classe_conta=account_class, id_tv=value_type,
                               use_cache=use_cache, verbose=verbose,
                               page_size=page_size, max_rows=max_rows)
