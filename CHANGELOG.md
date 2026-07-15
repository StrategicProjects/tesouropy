# Changelog

All notable changes to **tesouropy** are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
