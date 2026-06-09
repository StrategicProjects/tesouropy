# SICONFI — Fiscal data

[SICONFI](https://apidatalake.tesouro.gov.br/docs/siconfi/) (Sistema de
Informações Contábeis e Fiscais do Setor Público Brasileiro) is the Treasury's
hub for subnational fiscal reporting. `tesouropy` covers the budget report
(RREO), the fiscal management report (RGF), annual accounts (DCA), the
accounting balances matrix (MSC), delivery extracts, and the reference tables.

## Entities and reference tables

Almost every SICONFI call needs an entity `id_ente` (an IBGE code). Start from
the entity list:

```python
import tesouropy as tn
import polars as pl

entes = tn.get_entes()          # or get_entities()
anexos = tn.get_anexos()        # which appendix exists for each report/sphere

# IBGE code for the state of Pernambuco
pe = entes.filter((pl.col("uf") == "PE") & (pl.col("esfera") == "E"))
pe_id = pe["cod_ibge"][0]
```

## RREO — Budget Execution Summary Report

Published bimonthly. `nr_periodo` is the bimester (1–6).

```python
rreo = tn.get_rreo(
    an_exercicio=2022, nr_periodo=6,
    co_tipo_demonstrativo="RREO", no_anexo="RREO-Anexo 01",
    co_esfera="E", id_ente=17,
)
```

!!! note "`co_esfera` is optional"
    Some entities (e.g. the Federal District constitutional fund) only return
    data when the sphere filter is **omitted**. If a sphere-filtered call comes
    back empty, retry with `co_esfera=None`.

## RGF — Fiscal Management Report

```python
rgf = tn.get_rgf(
    an_exercicio=2022, in_periodicidade="Q", nr_periodo=3,
    co_tipo_demonstrativo="RGF", no_anexo="RGF-Anexo 01",
    co_esfera="E", co_poder="E", id_ente=17,
)
```

- `in_periodicidade`: `"Q"` (four-monthly) or `"S"` (semi-annual).
- `co_poder` (branch): `"E"` executive, `"L"` legislative, `"J"` judiciary,
  `"M"` public ministry, `"D"` public defender.

## DCA — Annual Accounts

```python
dca = tn.get_dca(an_exercicio=2022, id_ente=17)
```

## MSC — Accounting Balances Matrix

Three entry points by account class: control (7–8), budgetary (5–6), and
equity/asset (1–4).

```python
msc = tn.get_msc_patrimonial(
    id_ente=17, an_referencia=2022, me_referencia=12,
    co_tipo_matriz="MSCC", classe_conta=1, id_tv="ending_balance",
)
```

- `co_tipo_matriz`: `"MSCC"` (monthly aggregate) or `"MSCE"` (annual closing).
- `id_tv`: `"beginning_balance"`, `"ending_balance"`, or `"period_change"`.

## Delivery status

```python
extrato = tn.get_extrato(id_ente=17, an_referencia=2022)
```

## State-wide panels (fault tolerant)

Assemble a panel across every municipality of a state in one call. Failures are
recorded, not fatal:

```python
rreo_es = tn.get_rreo_for_state(
    state_uf="ES", an_exercicio=2021, nr_periodo=6,
    co_tipo_demonstrativo="RREO", no_anexo="RREO-Anexo 01",
)
getattr(rreo_es, "failed", None)   # municipalities that errored, if any
```

The same pattern exists for `get_dca_for_state` and `get_rgf_for_state` (and
their English aliases `*_for_state`).

## Functions

| Portuguese | English |
|---|---|
| `get_entes` | `get_entities` |
| `get_anexos` | `get_annexes` |
| `get_dca` | `get_annual_accounts` |
| `get_dca_for_state` | `get_annual_accounts_for_state` |
| `get_extrato` | `get_delivery_status` |
| `get_rreo` | `get_budget_report` |
| `get_rreo_for_state` | `get_budget_report_for_state` |
| `get_rgf` | `get_fiscal_report` |
| `get_rgf_for_state` | `get_fiscal_report_for_state` |
| `get_msc_controle` | `get_msc_control` |
| `get_msc_orcamentaria` | `get_msc_budget` |
| `get_msc_patrimonial` | `get_msc_equity` |

See the full signatures in the [Reference](../reference.md#siconfi).
