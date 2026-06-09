# SADIPEM — Public debt

The [SADIPEM](https://apidatalake.tesouro.gov.br/docs/sadipem/) API exposes the
Public Debt Verification Letters (PVL) system: requests for approval of credit
operations and debt by subnational entities, plus their schedules and capacity
results.

## Workflow

1. Search PVLs and pick an `id_pleito`.
2. Use that `id_pleito` in the detail functions.

```python
import tesouropy as tn

# 1. Search all PVLs for Pernambuco
pvl_pe = tn.get_pvl(uf="PE")          # or get_debt_requests(state="PE")

# 2. Pick an id_pleito
id_pleito = pvl_pe["id_pleito"][0]

# 3. Detail queries
liberacoes = tn.get_opc_cronograma_liberacoes(id_pleito=id_pleito)
pagamentos = tn.get_opc_cronograma_pagamentos(id_pleito=id_pleito)
cambio     = tn.get_opc_taxa_cambio(id_pleito=id_pleito)
cdp        = tn.get_res_cdp(id_pleito=id_pleito)
res_pgto   = tn.get_res_cronograma_pagamentos(id_pleito=id_pleito)
```

## Processing status (approved non-credit operations)

`get_pvl_tramitacao` only returns data for PVLs with status `"Deferido"`. For
other PVLs it returns an empty DataFrame — so filter first:

```python
import polars as pl

deferidos = pvl_pe.filter(pl.col("status") == "Deferido")
if deferidos.height:
    status = tn.get_pvl_tramitacao(id_pleito=deferidos["id_pleito"][0])
```

## Functions

| Portuguese | English |
|---|---|
| `get_pvl` | `get_debt_requests` |
| `get_pvl_tramitacao` | `get_pvl_status` |
| `get_opc_cronograma_liberacoes` | `get_credit_release_schedule` |
| `get_opc_cronograma_pagamentos` | `get_credit_payment_schedule` |
| `get_opc_taxa_cambio` | `get_credit_exchange_rate` |
| `get_res_cdp` | `get_debt_capacity` |
| `get_res_cronograma_pagamentos` | `get_debt_payment_schedule` |

See the full signatures in the [Reference](../reference.md#sadipem).
