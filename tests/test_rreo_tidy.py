"""Tests for the RREO tidy layer (layout reconciliation across years)."""

import polars as pl
import pytest

from tesouropy import rreo_layout, rreo_normalize_columns, tidy_rreo
from tesouropy._core import TesouroError


def test_rreo_layout_has_expected_columns():
    layout = rreo_layout()
    assert set(layout.columns) >= {
        "topic", "regime", "first_year", "last_year", "co_esfera",
        "no_anexo", "conta_match", "indicador",
    }
    assert "previdencia" in layout["topic"].to_list()


def test_rreo_normalize_columns():
    demo = pl.DataFrame(
        {
            "coluna": [
                "DESPESAS LIQUIDADAS ATÉ O BIMESTRE / 2023",
                "DESPESAS LIQUIDADAS ATÉ O BIMESTRE",
                "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS EM 2023",
            ]
        }
    )
    out = rreo_normalize_columns(demo)
    assert out["coluna_padrao"].to_list() == [
        "DESPESAS LIQUIDADAS ATÉ O BIMESTRE",
        "DESPESAS LIQUIDADAS ATÉ O BIMESTRE",
        "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS",
    ]
    assert out["coluna_ano"].to_list() == [2023, None, 2023]


def test_rreo_normalize_requires_coluna():
    with pytest.raises(TesouroError, match="coluna"):
        rreo_normalize_columns(pl.DataFrame({"x": [1]}))


def test_tidy_rreo_matches_across_layout_drift():
    # RGPS appendix moved from 04.3 (<=2022) to 04.4 (2023+); the conta label
    # also carries drifting Roman-numeral formula notation. tidy_rreo should
    # match both years to the same indicator.
    data = pl.DataFrame(
        {
            "exercicio": [2022, 2023, 2022],
            "conta": [
                "RESULTADO PREVIDENCIÁRIO RGPS (VII) = (III - VI)",
                "RESULTADO PREVIDENCIÁRIO RGPS (VIII) = (IV - VII)",
                "ALGUMA OUTRA CONTA QUALQUER",
            ],
            "coluna": ["Até o Bimestre", "Até o Bimestre", "Até o Bimestre"],
            "valor": [10.0, 20.0, 99.0],
        }
    )
    out = tidy_rreo(data, topic="previdencia", regime="rgps")
    assert out.height == 2
    assert set(out["indicador"].to_list()) == {"resultado_previdenciario_rgps"}
    assert sorted(out["valor"].to_list()) == [10.0, 20.0]
    assert out.columns[:2] == ["indicador", "regime"]


def test_tidy_rreo_unknown_topic_raises():
    data = pl.DataFrame(
        {"exercicio": [2022], "conta": ["x"], "coluna": ["y"], "valor": [1.0]}
    )
    with pytest.raises(TesouroError, match="No layout entry"):
        tidy_rreo(data, topic="does_not_exist")


def test_tidy_rreo_missing_columns_raises():
    with pytest.raises(TesouroError, match="missing required column"):
        tidy_rreo(pl.DataFrame({"exercicio": [2022]}), topic="previdencia")
