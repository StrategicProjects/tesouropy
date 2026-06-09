# Getting started

This page walks through the conventions shared by every function in
`tesouropy`: the bilingual interface, the polars output, caching, retries,
logging, and the fault-tolerance contract.

## Install and import

```bash
pip install tesouropy
```

```python
import tesouropy as tn
import polars as pl
```

## Bilingual interface (PT/EN)

Almost every function has **two names**: a Portuguese name with Portuguese
parameters, and an English alias mapping English parameter names onto the
Portuguese ones. They return identical data — pick whichever you prefer.

```python
# Portuguese
rreo = tn.get_rreo(
    an_exercicio=2022, nr_periodo=6,
    co_tipo_demonstrativo="RREO", no_anexo="RREO-Anexo 01",
    co_esfera="E", id_ente=17,
)

# English (same call, same result)
rreo = tn.get_budget_report(
    fiscal_year=2022, period=6,
    report_type="RREO", appendix="RREO-Anexo 01",
    sphere="E", entity_id=17,
)
```

!!! tip "Always call with keyword arguments"
    Function signatures put required parameters first (Python forbids a
    required parameter after one with a default), so the positional order may
    differ slightly from the R package. Calling with keywords keeps your code
    unambiguous and stable.

## polars output

Every fetch returns a [polars](https://pola.rs) `DataFrame` with tidy,
snake_case, accent-folded column names. Use the full polars API to wrangle it:

```python
entes = tn.get_entes()

# Municipalities of Pernambuco, biggest first
(
    entes
    .filter((pl.col("uf") == "PE") & (pl.col("esfera") == "M"))
    .sort("populacao", descending=True)
    .select("cod_ibge", "ente", "populacao")
    .head()
)
```

## Caching

Every HTTP request is cached **in memory** by default (`use_cache=True`), keyed
by URL + query parameters. Repeated calls in the same session are instant. Clear
the cache with:

```python
tn.tesouropy_clear_cache()
```

Pass `use_cache=False` to force a fresh request.

## Retries

Transient failures are retried automatically: **5 attempts** with progressive
backoff (3 → 6 → 9 → 12 s) on HTTP 429/500/502/503/504 and connection errors.
Non-retryable errors (400, 404, …) fail fast with an actionable message.

## Logging and verbosity

The package logs progress through the `"tesouropy"` logger, attached to a
`NullHandler`, so importing it is **silent by default**. Opt in to see progress:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

To log the full request URL of each call (handy for debugging or pasting into a
browser), pass `verbose=True` per call, or set it globally:

```python
tn.set_verbose(True)
```

## Limiting rows while exploring

Large datasets (CUSTOS, broad SICONFI queries) can be capped with `max_rows`
and tuned with `page_size`:

```python
sample = tn.get_custos_pessoal_ativo(ano=2023, mes=6, max_rows=100)
```

## Fault tolerance

Two families of functions never throw away data they already fetched.

### Partial pagination

If a page **after the first** fails, you get the rows fetched so far, flagged:

```python
df = tn.get_custos_pessoal_ativo(ano=2023)
if getattr(df, "partial", False):
    print("incomplete:", df.last_page_error)
```

### State-wide loops

The `*_for_state` helpers fetch data for every municipality of a state. If one
municipality fails after all retries, the failure is recorded and the loop
continues:

```python
rreo_es = tn.get_rreo_for_state(
    state_uf="ES", an_exercicio=2021, nr_periodo=6,
    co_tipo_demonstrativo="RREO", no_anexo="RREO-Anexo 01",
)

getattr(rreo_es, "failed", None)    # DataFrame of failed municipalities, if any
getattr(rreo_es, "no_data", None)   # municipalities that returned 0 rows
```

!!! warning "Metadata attributes are transient"
    `partial`, `failed`, `no_data` and `last_page_error` are attached to the
    returned DataFrame instance. Most polars operations return a *new*
    DataFrame that will not carry them, so read them right after the call.

## Where to next

- [SICONFI](guides/siconfi.md) — fiscal reports and entities
- [CUSTOS](guides/custos.md) — federal cost data
- [SADIPEM](guides/sadipem.md) — public debt
- [SIORG](guides/siorg.md) — organizational structure
- [Transferências](guides/transferencias.md) — constitutional transfers
- [SIOPE](guides/siope.md) — education spending
- [RREO longitudinal](how-to/rreo-longitudinal.md) — coherent series across years
