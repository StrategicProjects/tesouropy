"""Deprecated function names.

In 0.2.0 the SICONFI report getters were renamed to make their scope explicit:
the single-entity getters gained the ``_ufs`` suffix and the state-wide sweeps
(every municipality of a UF) moved from ``_for_state`` to ``_municipios`` /
``_municipalities``. The old names below still work but emit a
:class:`DeprecationWarning` and forward to the new names. They are kept for at
least one release cycle for backward compatibility.
"""

from __future__ import annotations

import warnings

from .siconfi import (
    get_annual_accounts_municipalities,
    get_annual_accounts_ufs,
    get_budget_report_municipalities,
    get_budget_report_ufs,
    get_dca_municipios,
    get_dca_ufs,
    get_fiscal_report_municipalities,
    get_fiscal_report_ufs,
    get_rgf_municipios,
    get_rgf_ufs,
    get_rreo_municipios,
    get_rreo_ufs,
)

__all__ = [
    "get_dca", "get_annual_accounts",
    "get_dca_for_state", "get_annual_accounts_for_state",
    "get_rreo", "get_budget_report",
    "get_rreo_for_state", "get_budget_report_for_state",
    "get_rgf", "get_fiscal_report",
    "get_rgf_for_state", "get_fiscal_report_for_state",
]


def _deprecated(new_func, old_name):
    """Build a wrapper for ``old_name`` that warns and forwards to ``new_func``."""

    def wrapper(*args, **kwargs):
        warnings.warn(
            f"{old_name}() is deprecated and will be removed in a future "
            f"release; use {new_func.__name__}() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return new_func(*args, **kwargs)

    wrapper.__name__ = old_name
    wrapper.__qualname__ = old_name
    wrapper.__doc__ = f"Deprecated alias for :func:`{new_func.__name__}`."
    return wrapper


# -- DCA ----------------------------------------------------------------------
get_dca = _deprecated(get_dca_ufs, "get_dca")
get_annual_accounts = _deprecated(get_annual_accounts_ufs, "get_annual_accounts")
get_dca_for_state = _deprecated(get_dca_municipios, "get_dca_for_state")
get_annual_accounts_for_state = _deprecated(
    get_annual_accounts_municipalities, "get_annual_accounts_for_state"
)

# -- RREO ---------------------------------------------------------------------
get_rreo = _deprecated(get_rreo_ufs, "get_rreo")
get_budget_report = _deprecated(get_budget_report_ufs, "get_budget_report")
get_rreo_for_state = _deprecated(get_rreo_municipios, "get_rreo_for_state")
get_budget_report_for_state = _deprecated(
    get_budget_report_municipalities, "get_budget_report_for_state"
)

# -- RGF ----------------------------------------------------------------------
get_rgf = _deprecated(get_rgf_ufs, "get_rgf")
get_fiscal_report = _deprecated(get_fiscal_report_ufs, "get_fiscal_report")
get_rgf_for_state = _deprecated(get_rgf_municipios, "get_rgf_for_state")
get_fiscal_report_for_state = _deprecated(
    get_fiscal_report_municipalities, "get_fiscal_report_for_state"
)
