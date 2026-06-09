# Transferências Constitucionais

The [Transferências Constitucionais](https://apiapex.tesouro.gov.br/aria/v1/transferencias_constitucionais/docs)
API reports constitutional transfers to states and municipalities.

!!! danger "Codes are internal Treasury codes — NOT IBGE codes"
    Every filter uses numeric codes from the Treasury's internal systems, which
    are **not** IBGE codes and **not** the two-letter UF abbreviation. Passing a
    UF abbreviation where a state code is expected makes the upstream API return
    HTTP 500 after a long retry budget — so `tesouropy` short-circuits that with
    a clear error. Always resolve codes through the dictionary functions first.

## Dictionaries first

```python
import tesouropy as tn
import polars as pl

tipos    = tn.get_tc_transferencias()   # transfer-type codes
estados  = tn.get_tc_estados()          # state codes (Treasury, not IBGE)

pe_code  = estados.filter(pl.col("nome") == "Pernambuco")["codigo"][0]

municipios = tn.get_tc_municipios(p_uf=pe_code)
recife = municipios.filter(pl.col("nome") == "Recife")["codigo"][0]
```

## Multi-value parameters

Multi-value parameters accept either a Python sequence or a colon-separated
string — both produce the same `"1:2:3"` query value:

```python
tn.get_tc_por_estados(p_estado=[1, 2], p_ano=2023, p_mes=[1, 2])
tn.get_tc_por_estados(p_estado="1:2", p_ano=2023, p_mes="1:2")   # identical
```

## By state and by municipality

```python
# By state (summary) and detailed
tc_pe   = tn.get_tc_por_estados(p_estado=pe_code, p_ano=2023)
tc_pe_d = tn.get_tc_por_estados_detalhe(p_estado=pe_code, p_ano=2023)

# By municipality (summary) and detailed
tc_rec   = tn.get_tc_por_municipio(p_estado=pe_code, p_municipio=recife, p_ano=2023)
tc_rec_d = tn.get_tc_por_municipio_detalhe(p_estado=pe_code, p_municipio=recife,
                                           p_ano=2023)
```

## Functions

| Portuguese | English |
|---|---|
| `get_tc_transferencias` | `get_tc_transfer_types` |
| `get_tc_estados` | `get_tc_states` |
| `get_tc_municipios` | `get_tc_municipalities` |
| `get_tc_por_estados` | `get_tc_by_state` |
| `get_tc_por_estados_detalhe` | `get_tc_by_state_detail` |
| `get_tc_por_municipio` | `get_tc_by_municipality` |
| `get_tc_por_municipio_detalhe` | `get_tc_by_municipality_detail` |

See the full signatures in the [Reference](../reference.md#transferencias-constitucionais).

A worked end-to-end example is in
[Transferências para municípios de PE](../applications/transferencias-pernambuco.md).
