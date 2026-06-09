# SIORG — Organizational structure

The [SIORG](https://api.siorg.economia.gov.br/) API describes the organizational
structure of the Brazilian Federal Executive Branch. Its codes are exactly the
ones the [CUSTOS](custos.md) API expects as `organizacao_n1/n2/n3`.

SIORG returns identifiers as URIs (e.g.
`https://.../id/unidade-organizacional/46`); `tesouropy` extracts the numeric
tail for you, so `codigo_unidade` columns are plain codes.

## Browse organizations

```python
import tesouropy as tn
import polars as pl

# All federal executive-branch organizations
orgaos = tn.get_siorg_orgaos(codigo_poder=1, codigo_esfera=1)

# Find a ministry and grab its code
mec = orgaos.filter(pl.col("sigla") == "MEC")
mec_code = mec["codigo_unidade"][0]
```

- `codigo_poder`: `1` Executive, `2` Legislative, `3` Judiciary.
- `codigo_esfera`: `1` Federal, `2` State/District, `3` Municipal.

## Drill into the structure tree

```python
# All sub-units of a given unit (flat DataFrame)
estrutura = tn.get_siorg_estrutura(codigo_unidade=46)   # e.g. AGU

# Navigate the hierarchy with codigo_unidade_pai
filhos = estrutura.filter(pl.col("codigo_unidade_pai") == "46")
```

## A single unit

```python
agu = tn.get_siorg_unidade(codigo_unidade=46)   # single-row DataFrame
```

## Feeding CUSTOS

```python
custos = tn.get_custos_pessoal_ativo(ano=2023, organizacao_n1=mec_code)
```

## Functions

| Portuguese | English |
|---|---|
| `get_siorg_orgaos` | `get_siorg_organizations` |
| `get_siorg_estrutura` | `get_siorg_structure` |
| `get_siorg_unidade` | `get_siorg_unit` |

See the full signatures in the [Reference](../reference.md#siorg).
