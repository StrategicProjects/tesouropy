# Changelog

All notable changes to **tesouropy** are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-10-29

Parity with `tesouror` 0.3.1 and 0.3.2.

### Fixed

- **`get_tc_por_municipio()` / `get_tc_by_municipality()` were unusable**: the
  Transferências Constitucionais API changed its municipal endpoint contract
  on the server side (2026-09) — parameter names became case-sensitive lower
  case with `p_municipio` in the singular, and responses became paginated.
  With the old upper-case names the server ignored every filter and timed out
  (HTTP 504) on every call. The functions now send the names the server
  expects and fetch every page (new arguments `page_size=1000` and
  `max_rows`); a page failing after the first returns the rows already
  fetched with `result.partial == True`.
- `get_tc_por_municipio_detalhe()` / `get_tc_by_municipality_detail()` keep
  the original contract, which that endpoint still uses (upper-case names,
  `P_MUNICIPIOS`, no pagination), now documented along with the ten-day
  installment columns it returns.

### Added

- Three new `tidy_rreo()` topics, probed live against SICONFI (2015-2026,
  all spheres): `"rcl"` (Receita Corrente Líquida, Anexo 03), `"balanco"`
  (Balanço Orçamentário, Anexo 01) and `"resultado"` (primary and nominal
  results, Anexo 06, across its three label eras including the 2023+
  com/sem RPPS split).
- The layout table gained a `cod_conta_match` column: a rule can match on
  SICONFI's stable semantic account code instead of the free-text label,
  which is ambiguous in Anexos 01 and 06. Topics matched on `cod_conta`
  require that column in the input (the raw SICONFI output carries it).
- `tidy_rreo()` matches rows only against the appendix each rule refers to
  when the input has an `anexo` column, preventing double counting with
  Anexo 14, which repeats accounts from other appendices under identical
  labels.
- New core helper `transferencias_fetch_all()` paginating `page`/`pageSize`
  endpoints with the same fault tolerance as `ords_fetch_all()`.

## [0.2.1] — 2026-07-14

### Added

- Citation metadata for archiving on Zenodo: `CITATION.cff` and `.zenodo.json`
  (authors with affiliations, keywords, related identifiers pointing to PyPI
  and to the origin R package `tesouror`).

### Fixed

- Author name spellings in the package metadata: "André Leite" (accent),
  "Marcos Wasiliew", and "Carlos Amorim".

## [0.2.0] — 2026-06-25

Parity with `tesouror` 0.3.0.

### Changed

- **Clearer SICONFI function names.** The single-entity report getters were
  renamed to make their scope explicit (e.g. `get_rreo` → `get_rreo_ufs`),
  and the state-wide municipality sweeps moved from the `_for_state` suffix to
  `_municipios` / `_municipalities` (PT / EN). The full set:
  `get_rreo`/`get_dca`/`get_rgf` → `*_ufs` (plus the English aliases
  `get_budget_report_ufs`, `get_annual_accounts_ufs`, `get_fiscal_report_ufs`);
  `get_*_for_state` → `get_*_municipios` / `get_*_municipalities`.

### Added

- **SIOPE entity-type filter.** All `get_siope_*` functions gained an optional
  `tipo` (`type` in the English aliases) argument that applies a server-side
  `DS_TIPO` filter, so you can fetch only the state-level row (`tipo="estado"`)
  or only the municipalities (`tipo="municipio"`) instead of the whole UF
  payload. Accepts PT/EN synonyms (accent- and case-insensitive) and combines
  with an existing `filter` via `and`.

### Deprecated

- The old SICONFI names (`get_rreo`, `get_dca`, `get_rgf`, `get_budget_report`,
  `get_annual_accounts`, `get_fiscal_report`, and their `_for_state` variants)
  still work but now emit a `DeprecationWarning` and forward to the new names.
  They will be removed in a future release.

[0.2.0]: https://github.com/StrategicProjects/tesouropy/releases/tag/v0.2.0

## [0.1.0] — 2026-06-09

Initial release. A Python port of the
[`tesouror`](https://github.com/StrategicProjects/tesouror) R package (parity
with R version 0.2.3).

### Added

- Unified access to six Brazilian National Treasury / federal APIs:
  **SICONFI** (RREO, RGF, DCA, MSC, entities), **CUSTOS**, **SADIPEM**,
  **Transferências Constitucionais**, **SIORG**, and **SIOPE**.
- Bilingual interface: every function has a Portuguese name and an English
  alias (86 `get_*` functions total).
- Core HTTP infrastructure ported from the R package:
  - In-memory response caching (`use_cache=True`), cleared with
    `tesouropy_clear_cache()`.
  - Retry with progressive backoff (5 attempts, 3/6/9/12s) on HTTP 429/5xx and
    connection failures, with actionable error messages.
  - ORDS pagination following `hasMore`, fault tolerant: partial results are
    returned with `result.partial` / `result.last_page_error` instead of being
    discarded on a mid-pagination failure.
  - Fault-tolerant state-wide loops (`*_for_state`): failures recorded on
    `result.failed`, empty results on `result.no_data`.
  - OData pagination for SIOPE; URI-code extraction for SIORG; numeric Treasury
    code guards for Transferências.
- RREO tidy layer: `rreo_layout()`, `rreo_normalize_columns()`, `tidy_rreo()`,
  reconciling SICONFI appendix/account label drift across years.
- Tidy [polars](https://pola.rs) DataFrame output with snake_case, accent-folded
  column names (a `janitor::clean_names()` analogue).
- Typed (`py.typed`) package; tests mocked with `responses`; CI across
  Python 3.9–3.13; PyPI publishing via GitHub Actions Trusted Publishing.

[0.1.0]: https://github.com/StrategicProjects/tesouropy/releases/tag/v0.1.0
