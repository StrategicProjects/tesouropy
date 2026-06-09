"""SADIPEM API functions (public debt and credit operations).

API docs: https://apidatalake.tesouro.gov.br/docs/sadipem/

Typical workflow:
    1. Search PVLs with :func:`get_pvl` / :func:`get_debt_requests`.
    2. Pick an ``id_pleito`` from the results.
    3. Use that ``id_pleito`` in the detail functions below.
"""

from __future__ import annotations

from ._core import INF, check_required, sadipem_fetch_all

__all__ = [
    "get_pvl", "get_debt_requests",
    "get_pvl_tramitacao", "get_pvl_status",
    "get_opc_cronograma_liberacoes", "get_credit_release_schedule",
    "get_opc_cronograma_pagamentos", "get_credit_payment_schedule",
    "get_opc_taxa_cambio", "get_credit_exchange_rate",
    "get_res_cdp", "get_debt_capacity",
    "get_res_cronograma_pagamentos", "get_debt_payment_schedule",
]


def get_pvl(uf=None, tipo_interessado=None, id_ente=None, use_cache=True,
            verbose=False, page_size=None, max_rows=INF):
    """Get public debt verification requests (PVL).

    Use the resulting ``id_pleito`` column to query the detail functions
    (:func:`get_pvl_tramitacao`, :func:`get_opc_cronograma_liberacoes`, ...).
    """
    params = {"uf": uf, "tipo_interessado": tipo_interessado, "id_ente": id_ente}
    return sadipem_fetch_all("/pvl", params, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_debt_requests(state=None, entity_type=None, entity_id=None,
                      use_cache=True, verbose=False, page_size=None,
                      max_rows=INF):
    """English alias for :func:`get_pvl`."""
    return get_pvl(uf=state, tipo_interessado=entity_type, id_ente=entity_id,
                   use_cache=use_cache, verbose=verbose, page_size=page_size,
                   max_rows=max_rows)


def get_pvl_tramitacao(id_pleito, use_cache=True, verbose=False, page_size=None,
                       max_rows=INF):
    """Get PVL processing status for approved non-credit operations.

    Only returns data for PVLs with status ``"Deferido"``; otherwise an empty
    DataFrame is returned.
    """
    check_required(id_pleito=id_pleito)
    return sadipem_fetch_all("/opnc-pvl-tramitacao-deferido",
                             {"id_pleito": id_pleito}, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_pvl_status(request_id, use_cache=True, verbose=False, page_size=None,
                   max_rows=INF):
    """English alias for :func:`get_pvl_tramitacao`."""
    check_required(request_id=request_id)
    return get_pvl_tramitacao(id_pleito=request_id, use_cache=use_cache,
                              verbose=verbose, page_size=page_size,
                              max_rows=max_rows)


def get_opc_cronograma_liberacoes(id_pleito, use_cache=True, verbose=False,
                                  page_size=None, max_rows=INF):
    """Get the credit operation release schedule for a PVL request."""
    check_required(id_pleito=id_pleito)
    return sadipem_fetch_all("/opc-cronograma-liberacoes",
                             {"id_pleito": id_pleito}, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_credit_release_schedule(request_id, use_cache=True, verbose=False,
                                page_size=None, max_rows=INF):
    """English alias for :func:`get_opc_cronograma_liberacoes`."""
    check_required(request_id=request_id)
    return get_opc_cronograma_liberacoes(id_pleito=request_id,
                                         use_cache=use_cache, verbose=verbose,
                                         page_size=page_size, max_rows=max_rows)


def get_opc_cronograma_pagamentos(id_pleito, use_cache=True, verbose=False,
                                  page_size=None, max_rows=INF):
    """Get the credit operation payment schedule for a PVL request."""
    check_required(id_pleito=id_pleito)
    return sadipem_fetch_all("/opc-cronograma-pagamentos",
                             {"id_pleito": id_pleito}, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_credit_payment_schedule(request_id, use_cache=True, verbose=False,
                                page_size=None, max_rows=INF):
    """English alias for :func:`get_opc_cronograma_pagamentos`."""
    check_required(request_id=request_id)
    return get_opc_cronograma_pagamentos(id_pleito=request_id,
                                         use_cache=use_cache, verbose=verbose,
                                         page_size=page_size, max_rows=max_rows)


def get_opc_taxa_cambio(id_pleito, use_cache=True, verbose=False, page_size=None,
                        max_rows=INF):
    """Get credit operation exchange rate data for a PVL request."""
    check_required(id_pleito=id_pleito)
    return sadipem_fetch_all("/opc-taxa-cambio", {"id_pleito": id_pleito},
                             use_cache=use_cache, verbose=verbose,
                             page_size=page_size, max_rows=max_rows)


def get_credit_exchange_rate(request_id, use_cache=True, verbose=False,
                             page_size=None, max_rows=INF):
    """English alias for :func:`get_opc_taxa_cambio`."""
    check_required(request_id=request_id)
    return get_opc_taxa_cambio(id_pleito=request_id, use_cache=use_cache,
                               verbose=verbose, page_size=page_size,
                               max_rows=max_rows)


def get_res_cdp(id_pleito, use_cache=True, verbose=False, page_size=None,
                max_rows=INF):
    """Get the Debt Capacity Result (CDP) for a PVL request."""
    check_required(id_pleito=id_pleito)
    return sadipem_fetch_all("/res-cdp", {"id_pleito": id_pleito},
                             use_cache=use_cache, verbose=verbose,
                             page_size=page_size, max_rows=max_rows)


def get_debt_capacity(request_id, use_cache=True, verbose=False, page_size=None,
                      max_rows=INF):
    """English alias for :func:`get_res_cdp`."""
    check_required(request_id=request_id)
    return get_res_cdp(id_pleito=request_id, use_cache=use_cache,
                       verbose=verbose, page_size=page_size, max_rows=max_rows)


def get_res_cronograma_pagamentos(id_pleito, use_cache=True, verbose=False,
                                  page_size=None, max_rows=INF):
    """Get the debt payment schedule result for a PVL request."""
    check_required(id_pleito=id_pleito)
    return sadipem_fetch_all("/res-cronograma-pagamentos",
                             {"id_pleito": id_pleito}, use_cache=use_cache,
                             verbose=verbose, page_size=page_size,
                             max_rows=max_rows)


def get_debt_payment_schedule(request_id, use_cache=True, verbose=False,
                              page_size=None, max_rows=INF):
    """English alias for :func:`get_res_cronograma_pagamentos`."""
    check_required(request_id=request_id)
    return get_res_cronograma_pagamentos(id_pleito=request_id,
                                         use_cache=use_cache, verbose=verbose,
                                         page_size=page_size, max_rows=max_rows)
