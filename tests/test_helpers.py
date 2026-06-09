"""Unit tests for the pure helpers in tesouropy._core."""

import polars as pl
import pytest

from tesouropy import _core
from tesouropy._core import (
    TesouroError,
    check_not_uf_abbrev,
    check_required,
    clean_name,
    clean_names,
    collapse_param,
    pad_siorg_code,
    siope_build_url,
)


def test_collapse_param_scalar_vector_none():
    assert collapse_param(None) is None
    assert collapse_param(2023) == "2023"
    assert collapse_param("1:2:3") == "1:2:3"
    assert collapse_param([1, 2, 3]) == "1:2:3"
    assert collapse_param(("a", "b")) == "a:b"


def test_pad_siorg_code():
    assert pad_siorg_code(None) is None
    assert pad_siorg_code(244) == "000244"
    assert pad_siorg_code("244") == "000244"
    assert pad_siorg_code(249) == "000249"


def test_uf_guard_rejects_abbreviation():
    with pytest.raises(TesouroError, match="Treasury state code"):
        check_not_uf_abbrev("PE", "p_estado")


def test_uf_guard_allows_numeric_and_none():
    check_not_uf_abbrev(None, "p_estado")  # no raise
    check_not_uf_abbrev(17, "p_estado")  # numeric code, no raise
    check_not_uf_abbrev([1, 2], "p_estado")  # vector, no raise


def test_check_required_raises_on_none():
    with pytest.raises(TesouroError, match="Missing required"):
        check_required(an_exercicio=None, id_ente=17)
    check_required(an_exercicio=2022, id_ente=17)  # no raise


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Cod IBGE", "cod_ibge"),
        ("codigoUnidadePai", "codigo_unidade_pai"),
        ("AN_EXERCICIO", "an_exercicio"),
        ("Instituição", "instituicao"),
        ("Valor (R$)", "valor_r"),
    ],
)
def test_clean_name(raw, expected):
    assert clean_name(raw) == expected


def test_clean_names_dedupes():
    df = pl.DataFrame({"a b": [1], "a-b": [2]})
    cleaned = clean_names(df)
    assert cleaned.columns == ["a_b", "a_b_2"]


def test_siope_build_url_string_and_numeric():
    url, query = siope_build_url(
        "Dados_Gerais_Siope",
        {"Ano_Consulta": 2023, "Num_Peri": 6, "Sig_UF": "PE"},
    )
    assert url.endswith(
        "/Dados_Gerais_Siope(Ano_Consulta=@Ano_Consulta,"
        "Num_Peri=@Num_Peri,Sig_UF=@Sig_UF)"
    )
    assert query["@Ano_Consulta"] == 2023
    assert query["@Sig_UF"] == "'PE'"  # strings are single-quoted
    assert query["$format"] == "json"


def test_cache_key_is_order_independent():
    k1 = _core._cache_key("http://x", {"a": 1, "b": 2})
    k2 = _core._cache_key("http://x", {"b": 2, "a": 1})
    assert k1 == k2
