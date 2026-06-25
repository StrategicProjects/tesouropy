# SIOPE — Education spending

[SIOPE](https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/aplicacao)
(Sistema de Informações sobre Orçamentos Públicos em Educação), maintained by
FNDE/MEC, reports education spending by states and municipalities through an
OData interface.

## Shared parameters

Most endpoints share three required parameters:

- `ano` / `year` — year (e.g. `2023`)
- `periodo` / `period` — bimester (1–6)
- `uf` / `state` — state abbreviation (e.g. `"PE"`)

`get_siope_remuneracao` additionally requires `mes` / `month`.

```python
import tesouropy as tn

dados = tn.get_siope_dados_gerais(ano=2023, periodo=6, uf="PE")
```

## Server-side filtering (recommended)

All functions accept OData `filter`, `orderby` and `select` to narrow results
**on the server** — much faster than downloading an entire state.

!!! tip "Use the original API column names (UPPERCASE)"
    In `filter`/`orderby`/`select`, columns use the original API names
    (uppercase), **not** the cleaned snake_case names of the returned
    DataFrame. To discover valid names, run a `max_rows=1` query and
    uppercase the resulting column names.

```python
# Fast: a single municipality, only the columns you need
resumo = tn.get_siope_dados_gerais(
    ano=2023, periodo=6, uf="PE",
    filter="COD_MUNI eq 2611606",
    select=["NOM_MUNI", "VAL_RECE_REAL", "VAL_DESP_PAGA"],
    orderby="NOM_MUNI asc",
)
```

### Filter by entity type (`tipo` / `type`)

The most common reason to narrow a SIOPE call is to keep only the state-level
row or only the municipalities. Pass `tipo` (`type` in the English aliases)
instead of writing the `DS_TIPO` OData clause by hand:

```python
# Only the state-level (UF) row
estado = tn.get_siope_dados_gerais(ano=2023, periodo=6, uf="PE", tipo="estado")

# Only the municipalities (English alias)
munis = tn.get_siope_general_data(year=2023, period=6, state="PE",
                                  type="municipality")
```

`tipo` accepts PT/EN synonyms (`"estado"`/`"uf"`/`"state"`,
`"municipio"`/`"municipality"`), is accent- and case-insensitive, and combines
with an existing `filter` via `and`.

## Endpoints

```python
tn.get_siope_dados_gerais(ano=2023, periodo=6, uf="PE")        # general data
tn.get_siope_responsaveis(ano=2023, periodo=6, uf="PE")        # officials
tn.get_siope_despesas(ano=2023, periodo=6, uf="PE")            # expenses
tn.get_siope_despesas_funcao(ano=2023, periodo=6, uf="PE")     # by function
tn.get_siope_indicadores(ano=2023, periodo=6, uf="PE")         # indicators
tn.get_siope_info_complementares(ano=2023, periodo=6, uf="PE") # supplementary
tn.get_siope_receitas(ano=2023, periodo=6, uf="PE")            # revenues
tn.get_siope_remuneracao(ano=2023, periodo=6, mes=12, uf="PE") # compensation
```

## Functions

| Portuguese | English |
|---|---|
| `get_siope_dados_gerais` | `get_siope_general_data` |
| `get_siope_responsaveis` | `get_siope_officials` |
| `get_siope_despesas` | `get_siope_expenses` |
| `get_siope_despesas_funcao` | `get_siope_expenses_by_function` |
| `get_siope_indicadores` | `get_siope_indicators` |
| `get_siope_info_complementares` | `get_siope_supplementary` |
| `get_siope_receitas` | `get_siope_revenues` |
| `get_siope_remuneracao` | `get_siope_compensation` |

See the full signatures in the [Reference](../reference.md#siope).
