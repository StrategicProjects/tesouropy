"""tesouropy — access Brazilian National Treasury open-data APIs from Python.

A Python port of the `tesouror <https://github.com/StrategicProjects/tesouror>`_
R package. Provides a unified interface to six government data sources:

* **SICONFI** — fiscal reports (RREO, RGF, DCA, MSC) and entity information.
* **CUSTOS** — federal government cost data.
* **SADIPEM** — public debt and credit operations.
* **Transferencias Constitucionais** — constitutional transfers to states and
  municipalities.
* **SIORG** — federal organizational structure.
* **SIOPE** — education spending data (FNDE/MEC).

Features automatic pagination, in-memory caching, retry logic with backoff, and
tidy `polars <https://pola.rs>`_ DataFrame output. Almost every function has a
Portuguese name and an English alias.
"""

from __future__ import annotations

from ._core import TesouroError, set_verbose, tesouropy_clear_cache
from .custos import (
    get_costs_active_staff,
    get_costs_depreciation,
    get_costs_other,
    get_costs_pensioners,
    get_costs_retired_staff,
    get_costs_transfers,
    get_custos_demais,
    get_custos_depreciacao,
    get_custos_pensionistas,
    get_custos_pessoal_ativo,
    get_custos_pessoal_inativo,
    get_custos_transferencias,
)
from .rreo_tidy import rreo_layout, rreo_normalize_columns, tidy_rreo
from .sadipem import (
    get_credit_exchange_rate,
    get_credit_payment_schedule,
    get_credit_release_schedule,
    get_debt_capacity,
    get_debt_payment_schedule,
    get_debt_requests,
    get_opc_cronograma_liberacoes,
    get_opc_cronograma_pagamentos,
    get_opc_taxa_cambio,
    get_pvl,
    get_pvl_status,
    get_pvl_tramitacao,
    get_res_cdp,
    get_res_cronograma_pagamentos,
)
from .siconfi import (
    get_anexos,
    get_annexes,
    get_annual_accounts,
    get_annual_accounts_for_state,
    get_budget_report,
    get_budget_report_for_state,
    get_dca,
    get_dca_for_state,
    get_delivery_status,
    get_entes,
    get_entities,
    get_extrato,
    get_fiscal_report,
    get_fiscal_report_for_state,
    get_msc_budget,
    get_msc_control,
    get_msc_controle,
    get_msc_equity,
    get_msc_orcamentaria,
    get_msc_patrimonial,
    get_rgf,
    get_rgf_for_state,
    get_rreo,
    get_rreo_for_state,
)
from .siope import (
    get_siope_compensation,
    get_siope_dados_gerais,
    get_siope_despesas,
    get_siope_despesas_funcao,
    get_siope_expenses,
    get_siope_expenses_by_function,
    get_siope_general_data,
    get_siope_indicadores,
    get_siope_indicators,
    get_siope_info_complementares,
    get_siope_officials,
    get_siope_receitas,
    get_siope_remuneracao,
    get_siope_responsaveis,
    get_siope_revenues,
    get_siope_supplementary,
)
from .siorg import (
    get_siorg_estrutura,
    get_siorg_orgaos,
    get_siorg_organizations,
    get_siorg_structure,
    get_siorg_unidade,
    get_siorg_unit,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "TesouroError",
    "set_verbose",
    "tesouropy_clear_cache",
    # SICONFI
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
    # CUSTOS
    "get_custos_pessoal_ativo", "get_costs_active_staff",
    "get_custos_pessoal_inativo", "get_costs_retired_staff",
    "get_custos_pensionistas", "get_costs_pensioners",
    "get_custos_demais", "get_costs_other",
    "get_custos_depreciacao", "get_costs_depreciation",
    "get_custos_transferencias", "get_costs_transfers",
    # SADIPEM
    "get_pvl", "get_debt_requests",
    "get_pvl_tramitacao", "get_pvl_status",
    "get_opc_cronograma_liberacoes", "get_credit_release_schedule",
    "get_opc_cronograma_pagamentos", "get_credit_payment_schedule",
    "get_opc_taxa_cambio", "get_credit_exchange_rate",
    "get_res_cdp", "get_debt_capacity",
    "get_res_cronograma_pagamentos", "get_debt_payment_schedule",
    # Transferencias
    "get_tc_transferencias", "get_tc_transfer_types",
    "get_tc_estados", "get_tc_states",
    "get_tc_municipios", "get_tc_municipalities",
    "get_tc_por_estados", "get_tc_by_state",
    "get_tc_por_estados_detalhe", "get_tc_by_state_detail",
    "get_tc_por_municipio", "get_tc_by_municipality",
    "get_tc_por_municipio_detalhe", "get_tc_by_municipality_detail",
    # SIORG
    "get_siorg_orgaos", "get_siorg_organizations",
    "get_siorg_estrutura", "get_siorg_structure",
    "get_siorg_unidade", "get_siorg_unit",
    # SIOPE
    "get_siope_dados_gerais", "get_siope_general_data",
    "get_siope_responsaveis", "get_siope_officials",
    "get_siope_despesas", "get_siope_expenses",
    "get_siope_despesas_funcao", "get_siope_expenses_by_function",
    "get_siope_indicadores", "get_siope_indicators",
    "get_siope_info_complementares", "get_siope_supplementary",
    "get_siope_receitas", "get_siope_revenues",
    "get_siope_remuneracao", "get_siope_compensation",
    # RREO tidy
    "rreo_layout", "rreo_normalize_columns", "tidy_rreo",
]

# Transferencias imports live at the bottom so the __all__ above can reference
# them; keep them grouped with the package's other public symbols.
from .transferencias import (  # noqa: E402
    get_tc_by_municipality,
    get_tc_by_municipality_detail,
    get_tc_by_state,
    get_tc_by_state_detail,
    get_tc_estados,
    get_tc_municipalities,
    get_tc_municipios,
    get_tc_por_estados,
    get_tc_por_estados_detalhe,
    get_tc_por_municipio,
    get_tc_por_municipio_detalhe,
    get_tc_states,
    get_tc_transfer_types,
    get_tc_transferencias,
)
