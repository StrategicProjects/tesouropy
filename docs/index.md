# tesouropy

**Access Brazilian National Treasury open-data APIs from Python.**

`tesouropy` is a Python port of the
[`tesouror`](https://github.com/StrategicProjects/tesouror) R package. It gives
you a single, consistent interface to six open-data sources of the Brazilian
National Treasury (*Tesouro Nacional*) and related federal government APIs,
returning tidy [polars](https://pola.rs) DataFrames.

| Domain | What it covers | API style |
|---|---|---|
| **SICONFI** | Fiscal reports — RREO, RGF, DCA, MSC — and entity info | ORDS (`hasMore`/`offset`) |
| **CUSTOS** | Federal government cost data | ORDS |
| **SADIPEM** | Public debt and credit operations (PVL) | ORDS |
| **Transferências Constitucionais** | Constitutional transfers to states/municipalities | Simple JSON |
| **SIORG** | Federal organizational structure | Simple JSON |
| **SIOPE** | Education spending data (FNDE/MEC) | OData |

## Highlights

- **Automatic pagination** — ORDS (`hasMore`) and OData (`$top`/`$skip`).
- **In-memory caching** — every request is cached by default.
- **Retry with backoff** — 5 attempts (3/6/9/12s) on HTTP 429/5xx and
  connection failures, with actionable error messages.
- **Fault-tolerant state-wide loops** — partial results instead of hard
  failures (`result.failed`, `result.no_data`).
- **Tidy output** — snake_case, accent-folded column names; polars DataFrames.
- **Bilingual interface** — every function has a Portuguese name and an English
  alias.

## Install

```bash
pip install tesouropy
```

Requires Python 3.9+. Runtime dependencies: `polars` and `requests`.

## A first taste

```python
import tesouropy as tn

entes = tn.get_entes()                       # all government entities

rreo = tn.get_budget_report_ufs(                 # English alias of get_rreo_ufs
    fiscal_year=2022, period=6,
    report_type="RREO", appendix="RREO-Anexo 01",
    sphere="E", entity_id=17,
)
```

Head to [Getting started](getting-started.md) for the full tour, or jump to an
[API guide](guides/siconfi.md). Every public function is documented in the
[Reference](reference.md).

## Relationship to the R package

`tesouropy` mirrors the public API of
[`tesouror`](https://github.com/StrategicProjects/tesouror) (CRAN): function
names, parameters, endpoints, pagination and fault-tolerance behaviour are kept
in sync. The idiomatic differences: R tibbles become polars DataFrames, and R
attributes (`attr(x, "partial")`, `attr(x, "failed")`) become instance
attributes (`x.partial`, `x.failed`).
