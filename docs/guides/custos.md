# CUSTOS — Federal costs

The [CUSTOS](https://apidatalake.tesouro.gov.br/docs/custos/) API exposes
federal government cost data, broken down into six categories: active staff,
retired staff, pensioners, other (non-personnel) costs, depreciation, and
transfers.

!!! warning "Always filter — the CUSTOS backend is slow"
    The server default is 250 rows/page and unfiltered queries return hundreds
    of thousands of rows, frequently timing out (HTTP 504). Always narrow your
    query by organization (`organizacao_n1` + `organizacao_n2`), time
    (`ano` + `mes`), and/or `natureza_juridica`. Use `max_rows` while
    exploring. `tesouropy` defaults to `page_size=500` for this API.

## Organization codes (SIORG)

CUSTOS filters by SIORG codes, which you look up with the
[SIORG](siorg.md) API. Codes are **auto-padded** to 6 digits, so you can pass
`244` or `"000244"` — both work.

```python
import tesouropy as tn

orgaos = tn.get_siorg_orgaos(codigo_poder=1, codigo_esfera=1)
# ... find the codigo_unidade for the ministry you want, then:

ativos = tn.get_custos_pessoal_ativo(
    ano=2023,
    organizacao_n1=244,   # MEC, auto-padded to "000244"
    organizacao_n2=249,   # INEP
)
```

## Categories

```python
tn.get_custos_pessoal_ativo(ano=2023, mes=6, organizacao_n1=244)    # active
tn.get_custos_pessoal_inativo(ano=2023, mes=6, organizacao_n1=244)  # retired
tn.get_custos_pensionistas(ano=2023, mes=12, organizacao_n1=244)    # pensioners
tn.get_custos_demais(ano=2023, mes=6, organizacao_n1=244)           # other
tn.get_custos_depreciacao(ano=2023, mes=6, organizacao_n1=244)      # depreciation
tn.get_custos_transferencias(ano=2023, mes=6, organizacao_n1=244)   # transfers
```

`natureza_juridica`: `1` Public Company, `2` Public Foundation, `3` Direct
Administration, `4` Autarchy, `6` Mixed Economy Company.

## If a query returns a partial result

On a mid-pagination timeout you still get the rows fetched so far:

```python
df = tn.get_custos_pessoal_ativo(ano=2023, organizacao_n1=244)
if getattr(df, "partial", False):
    # lower page_size and/or add a `mes` filter, then retry
    df = tn.get_custos_pessoal_ativo(ano=2023, mes=6, organizacao_n1=244,
                                     page_size=250)
```

## Functions

| Portuguese | English |
|---|---|
| `get_custos_pessoal_ativo` | `get_costs_active_staff` |
| `get_custos_pessoal_inativo` | `get_costs_retired_staff` |
| `get_custos_pensionistas` | `get_costs_pensioners` |
| `get_custos_demais` | `get_costs_other` |
| `get_custos_depreciacao` | `get_costs_depreciation` |
| `get_custos_transferencias` | `get_costs_transfers` |

See the full signatures in the [Reference](../reference.md#custos).
