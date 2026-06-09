# Transferências Constitucionais para municípios de Pernambuco

Um exemplo de ponta a ponta: levantar as transferências constitucionais para os
municípios de Pernambuco em um ano, partindo dos dicionários de códigos do
Tesouro até um ranking final.

!!! danger "Códigos do Tesouro, não IBGE"
    Lembre: os filtros desta API usam **códigos internos do Tesouro**, não
    códigos IBGE nem a sigla da UF. Sempre resolva os códigos pelos dicionários
    primeiro (veja o [guia de Transferências](../guides/transferencias.md)).

## 1. Resolver os códigos

```python
import tesouropy as tn
import polars as pl

estados = tn.get_tc_estados()
pe_code = estados.filter(pl.col("nome") == "Pernambuco")["codigo"][0]

municipios = tn.get_tc_municipios(p_uf=pe_code)
print(municipios.height, "municípios em PE")
```

## 2. Buscar as transferências do ano

```python
tc = tn.get_tc_por_municipio(p_estado=pe_code, p_ano=2023)
```

## 3. Ranking dos maiores recebedores

O esquema de colunas exato depende da resposta da API; ajuste os nomes conforme
o que `tc.columns` mostrar. Supondo colunas de nome do município e valor:

```python
ranking = (
    tc
    .group_by("nome")
    .agg(pl.col("valor").sum().alias("total"))
    .sort("total", descending=True)
    .head(10)
)
print(ranking)
```

## 4. Detalhamento de um município

```python
recife = municipios.filter(pl.col("nome") == "Recife")["codigo"][0]

detalhe = tn.get_tc_por_municipio_detalhe(
    p_estado=pe_code, p_municipio=recife, p_ano=2023,
)
```

## Dica de desempenho

Os dicionários (`get_tc_estados`, `get_tc_municipios`, `get_tc_transferencias`)
são cacheados em memória após a primeira chamada na sessão, então reusá-los em
um laço sobre vários anos ou estados não gera novas requisições.
