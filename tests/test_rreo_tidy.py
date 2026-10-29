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


def test_rreo_layout_rules_have_exactly_one_matching_key():
    layout = rreo_layout()
    assert set(layout["topic"].to_list()) == {
        "previdencia", "rcl", "balanco", "resultado",
    }
    conta = layout["conta_match"].str.len_chars() > 0
    cod = layout["cod_conta_match"].str.len_chars() > 0
    assert (conta ^ cod).all()


def test_tidy_rreo_rcl_across_years_and_anexo_guard():
    data = pl.DataFrame(
        {
            "exercicio": [2015, 2024, 2024, 2024],
            "anexo": [
                "RREO-Anexo 03", "RREO-Anexo 03", "RREO-Anexo 03",
                # Anexo 14 repeats the RCL account: must NOT match
                "RREO-Anexo 14",
            ],
            "conta": [
                "RECEITA CORRENTE LÍQUIDA (III) = (I - II)",
                "RECEITA CORRENTE LÍQUIDA (III) = (I - II)",
                # 2024 drifted Roman numerals (was "(VII) = (V - VI)")
                "RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES"
                " DA DESPESA COM PESSOAL (IX) = (V - VI - VII - VIII)",
                "RECEITA CORRENTE LÍQUIDA (III) = (I - II)",
            ],
            "coluna": ["TOTAL (ÚLTIMOS 12 MESES)"] * 4,
            "valor": [10.0, 20.0, 30.0, 99.0],
        }
    )
    out = tidy_rreo(data, topic="rcl")
    assert sorted(out["valor"].to_list()) == [10.0, 20.0, 30.0]
    assert set(out["regime"].to_list()) == {"total", "ajustada_pessoal"}

    total = tidy_rreo(data, topic="rcl", regime="total")
    assert sorted(total["exercicio"].to_list()) == [2015, 2024]


def test_tidy_rreo_balanco_matches_on_cod_conta():
    data = pl.DataFrame(
        {
            "exercicio": [2015, 2015, 2015, 2024, 2024],
            "anexo": ["RREO-Anexo 01"] * 5,
            "conta": [
                "SUBTOTAL DAS RECEITAS (III) = (I + II)",
                # old era: "TOTAL" on BOTH sides -> ambiguous, not in layout
                "TOTAL (VII) = (V + VI)",
                "TOTAL (XIV) = (XII + XIII)",
                # same label, different codes: main vs intra not lumped
                "RECEITAS CORRENTES",
                "RECEITAS CORRENTES",
            ],
            "cod_conta": [
                "SubtotalDasReceitas", "TotalReceitas", "TotalDespesas",
                "ReceitasCorrentes", "ReceitasCorrentesIntra",
            ],
            "coluna": ["RECEITAS REALIZADAS ATÉ O BIMESTRE"] * 5,
            "valor": [10.0, 11.0, 12.0, 30.0, 31.0],
        }
    )
    out = tidy_rreo(data, topic="balanco")
    assert sorted(out["valor"].to_list()) == [10.0, 30.0]
    assert set(out["regime"].to_list()) == {"receitas", "receitas_correntes"}


def test_tidy_rreo_resultado_separates_collapsing_labels():
    # 2023+ state/municipal labels "(COM RPPS)" and "(SEM RPPS)" clean to the
    # same text; cod_conta keeps the series apart across the three eras.
    data = pl.DataFrame(
        {
            "exercicio": [2016, 2016, 2020, 2024, 2024],
            "anexo": ["RREO-Anexo 06"] * 5,
            "conta": [
                "RESULTADO PRIMÁRIO (XIX) = (VII - XVIII)",
                "RESULTADO PRIMÁRIO DA UNIÃO (X) = (V - VI - VII)",
                "RESULTADO PRIMÁRIO - Acima da Linha (XXIV) = (...)",
                "RESULTADO PRIMÁRIO (COM RPPS) - Acima da Linha (XXXIV)",
                "RESULTADO PRIMÁRIO (SEM RPPS) - Acima da Linha (XXXV)",
            ],
            "cod_conta": [
                "RREO6ResultadoPrimarioEstadosMunicipios",
                "RREO6ResultadoPrimarioDaUniao",
                "RREO6ResultadoPrimarioEstadosMunicipios",
                "ResultadoPrimarioComRPPSAcimaDaLinha",
                "ResultadoPrimarioSemRPPSAcimaDaLinha",
            ],
            "coluna": ["Até o Bimestre / 2024"] * 5,
            "valor": [1.0, 2.0, 3.0, 40.0, 50.0],
        }
    )
    primario = tidy_rreo(data, topic="resultado", regime="primario")
    assert sorted(primario["valor"].to_list()) == [1.0, 2.0, 3.0]
    assert set(primario["indicador"].to_list()) == {"resultado_primario"}

    com = tidy_rreo(data, topic="resultado", regime="primario_com_rpps")
    assert com["valor"].to_list() == [40.0]
    sem = tidy_rreo(data, topic="resultado", regime="primario_sem_rpps")
    assert sem["valor"].to_list() == [50.0]


def test_tidy_rreo_cod_topic_requires_cod_conta_column():
    data = pl.DataFrame(
        {
            "exercicio": [2024],
            "conta": ["SUBTOTAL DAS RECEITAS (III) = (I + II)"],
            "coluna": ["RECEITAS REALIZADAS"],
            "valor": [1.0],
        }
    )
    with pytest.raises(TesouroError, match="cod_conta"):
        tidy_rreo(data, topic="balanco")


def test_tidy_rreo_unknown_topic_raises():
    data = pl.DataFrame(
        {"exercicio": [2022], "conta": ["x"], "coluna": ["y"], "valor": [1.0]}
    )
    with pytest.raises(TesouroError, match="No layout entry"):
        tidy_rreo(data, topic="does_not_exist")


def test_tidy_rreo_missing_columns_raises():
    with pytest.raises(TesouroError, match="missing required column"):
        tidy_rreo(pl.DataFrame({"exercicio": [2022]}), topic="previdencia")
