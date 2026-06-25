# tesouropy

[![PyPI](https://img.shields.io/pypi/v/tesouropy?cacheSeconds=600)](https://pypi.org/project/tesouropy/)
[![Python versions](https://img.shields.io/pypi/pyversions/tesouropy?cacheSeconds=600)](https://pypi.org/project/tesouropy/)
[![CI](https://github.com/StrategicProjects/tesouropy/actions/workflows/ci.yml/badge.svg)](https://github.com/StrategicProjects/tesouropy/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-strategicprojects.github.io-teal)](https://strategicprojects.github.io/tesouropy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

📖 **Documentation & guides: <https://strategicprojects.github.io/tesouropy/>**

**Access Brazilian National Treasury open-data APIs from Python.**

`tesouropy` is a Python port of the
[`tesouror`](https://github.com/StrategicProjects/tesouror) R package. It gives
you a single, consistent interface to six open-data sources of the Brazilian
National Treasury (*Tesouro Nacional*) and related federal government APIs,
returning tidy [polars](https://pola.rs) DataFrames.

| Domain | What it covers | API style |
|---|---|---|
| **SICONFI** | Fiscal reports — RREO, RGF, DCA, MSC — and entity info | ORDS (`hasMore`/`offset` pagination) |
| **CUSTOS** | Federal government cost data | ORDS |
| **SADIPEM** | Public debt and credit operations (PVL) | ORDS |
| **Transferências Constitucionais** | Constitutional transfers to states/municipalities | Simple JSON |
| **SIORG** | Federal organizational structure | Simple JSON |
| **SIOPE** | Education spending data (FNDE/MEC) | OData |

Features: **automatic pagination**, **in-memory caching**, **retry with
backoff**, **fault-tolerant state-wide loops** (partial results instead of
hard failures), and **tidy snake_case output**.

## Installation

```bash
pip install tesouropy
```

Requires Python 3.9+. Runtime dependencies: `polars` and `requests`.

## Bilingual interface (PT/EN)

Almost every function has **two names**: a Portuguese name with Portuguese
parameters, and an English alias that maps English parameter names onto the
Portuguese ones. Pick whichever you prefer — they return identical data.

```python
import tesouropy as tn

# Portuguese
rreo = tn.get_rreo_ufs(
    an_exercicio=2022, nr_periodo=6,
    co_tipo_demonstrativo="RREO", no_anexo="RREO-Anexo 01",
    co_esfera="E", id_ente=17,
)

# English (same call)
rreo = tn.get_budget_report_ufs(
    fiscal_year=2022, period=6,
    report_type="RREO", appendix="RREO-Anexo 01",
    sphere="E", entity_id=17,
)
```

## Quick start

```python
import tesouropy as tn

# List all government entities (states, municipalities, DF)
entes = tn.get_entes()

# Fiscal Management Report (RGF) for a state
rgf = tn.get_rgf_ufs(
    an_exercicio=2022, in_periodicidade="Q", nr_periodo=3,
    co_tipo_demonstrativo="RGF", no_anexo="RGF-Anexo 01",
    co_esfera="E", co_poder="E", id_ente=17,
)

# Public debt verification requests for a state, then a detail query
pvl = tn.get_pvl(uf="PE")
schedule = tn.get_opc_cronograma_pagamentos(id_pleito=pvl["id_pleito"][0])

# Education spending (SIOPE), filtered server-side for speed
recife = tn.get_siope_dados_gerais(
    ano=2023, periodo=6, uf="PE", filter="NOM_MUNI eq 'Recife'",
)

# Federal cost data (CUSTOS) — always filter; SIORG codes auto-padded
custos = tn.get_custos_pessoal_ativo(ano=2023, organizacao_n1=244)
```

### State-wide panels (fault tolerant)

The `*_for_state` helpers fetch data for every municipality of a state, looping
with fault tolerance: if a municipality call fails after all retries, the
failure is recorded and the loop continues.

```python
rreo_es = tn.get_rreo_municipios(
    state_uf="ES", an_exercicio=2021, nr_periodo=6,
    co_tipo_demonstrativo="RREO", no_anexo="RREO-Anexo 01",
)

# Inspect partial failures / no-data municipalities
getattr(rreo_es, "failed", None)    # DataFrame of failed calls, if any
getattr(rreo_es, "no_data", None)   # municipalities that returned 0 rows
```

Similarly, ORDS pagination is fault tolerant: if a page after the first fails,
you get a partial DataFrame with `result.partial == True` and
`result.last_page_error` set, rather than losing everything fetched so far.

### Reconciling RREO layout drift across years

SICONFI relabels RREO appendices and accounts over time. `tidy_rreo()` uses a
bundled layout table to assemble a coherent series across years:

```python
import polars as pl

frames = []
for yr in range(2019, 2024):
    rule = tn.rreo_layout().filter(
        (pl.col("topic") == "previdencia") & (pl.col("regime") == "rgps")
        & (pl.col("first_year") <= yr) & (pl.col("last_year") >= yr)
    )
    frames.append(tn.get_rreo_ufs(
        an_exercicio=yr, nr_periodo=6, co_tipo_demonstrativo="RREO",
        no_anexo=rule["no_anexo"][0], co_esfera="U", id_ente=1,
    ))
rreo = pl.concat(frames, how="diagonal_relaxed")
serie = tn.tidy_rreo(rreo, topic="previdencia", regime="rgps")
```

## Caching, retries and logging

- **Cache**: every HTTP request is cached in memory by default
  (`use_cache=True`). Clear it with `tn.tesouropy_clear_cache()`.
- **Retries**: 5 attempts with progressive backoff (3/6/9/12s) on HTTP
  429/5xx and connection failures.
- **Logging**: the package logs progress through the `"tesouropy"` logger with
  a `NullHandler`, so it is silent by default. Enable it with:

  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  ```

  Pass `verbose=True` (or call `tn.set_verbose(True)`) to log the full request
  URL of each call — handy for debugging.

## Relationship to the R package

`tesouropy` mirrors the public API of
[`tesouror`](https://github.com/StrategicProjects/tesouror) (CRAN). The
function names, parameters, endpoints, pagination and fault-tolerance behaviour
are kept in sync. The main idiomatic differences: R tibbles become polars
DataFrames, and R attributes (`attr(x, "partial")`, `attr(x, "failed")`) become
instance attributes (`x.partial`, `x.failed`).

## License

MIT © tesouropy authors. See [LICENSE](LICENSE).
