# RREO longitudinal — handling layout drift across years

SICONFI relabels RREO appendices, columns and account codes over time. The same
concept appears under a different appendix number, a different column suffix, or
a different Roman-numeral formula from one year to the next. Stitching a
multi-year series together by hand is error-prone.

`tesouropy` ships a small layout reference table and three helpers to do it
reliably:

- `rreo_layout()` — the bundled `(topic, regime, year_range) → appendix, key`
  table.
- `rreo_normalize_columns()` — strips drifting `/ YYYY` / `EM YYYY` suffixes
  from the `coluna` field.
- `tidy_rreo()` — filters to a topic and matches accounts on a year-stable,
  accent-folded key, returning a coherent series with a stable `indicador`.

## The layout table

```python
import tesouropy as tn

tn.rreo_layout()
```

Each row maps a topic/regime and a year range to the correct appendix
(`no_anexo`) and a normalized account-matching key (`conta_match`). For example,
the federal RGPS appendix moved from `RREO-Anexo 04.3 - RGPS` (up to 2022) to
`RREO-Anexo 04.4 - RGPS` (2023+) — the table knows this.

Currently supported topic: **`"previdencia"`** (federal RGPS, RPPS civis, FCDF,
militares inativos — União sphere). Contributions adding new topics to the
layout table are welcome.

## Assembling a multi-year series

Use the layout to fetch the *right* appendix for each year, concatenate, then
`tidy_rreo()`:

```python
import polars as pl
import tesouropy as tn

layout = tn.rreo_layout()

frames = []
for yr in range(2019, 2024):
    rule = layout.filter(
        (pl.col("topic") == "previdencia")
        & (pl.col("regime") == "rgps")
        & (pl.col("first_year") <= yr)
        & (pl.col("last_year") >= yr)
    )
    frames.append(
        tn.get_rreo_ufs(
            an_exercicio=yr, nr_periodo=6,
            co_tipo_demonstrativo="RREO",
            no_anexo=rule["no_anexo"][0],
            co_esfera="U", id_ente=1,
        )
    )

rreo = pl.concat(frames, how="diagonal_relaxed")

serie = (
    tn.tidy_rreo(rreo, topic="previdencia", regime="rgps")
    .filter(
        (pl.col("coluna_padrao") == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE")
        & (pl.col("coluna_ano").is_null() | (pl.col("coluna_ano") == pl.col("exercicio")))
    )
    .select("exercicio", "indicador", "valor")
    .sort("exercicio")
)
```

`tidy_rreo()` adds:

- `indicador` — a stable indicator name (e.g.
  `"resultado_previdenciario_rgps"`), constant across years even when SICONFI
  relabelled the account.
- `regime` — the matched regime.
- `coluna_padrao` / `coluna_ano` — from `rreo_normalize_columns()`, so you can
  distinguish the current-year column from a comparative previous-year column.

## Why the matching is robust

`tidy_rreo()` reduces each `conta` to a key by dropping everything from the
first `(` (the drifting Roman-numeral formula), stripping diacritics,
lowercasing and squishing whitespace. So
`"RESULTADO PREVIDENCIÁRIO RGPS (VII) = (III - VI)"` (2022) and
`"RESULTADO PREVIDENCIÁRIO RGPS (VIII) = (IV - VII)"` (2023) both reduce to
`resultado previdenciario rgps` and match the same layout rule.
