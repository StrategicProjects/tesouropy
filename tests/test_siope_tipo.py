"""Tests for the SIOPE ``tipo``/``type`` convenience filter."""

import responses
import pytest

import tesouropy
from tesouropy import _core
from tesouropy.siope import _siope_tipo_filter


def test_tipo_filter_maps_state_synonyms():
    assert _siope_tipo_filter("estado") == "DS_TIPO eq 'Estado'"
    assert _siope_tipo_filter("Estado") == "DS_TIPO eq 'Estado'"
    assert _siope_tipo_filter("UF") == "DS_TIPO eq 'Estado'"
    assert _siope_tipo_filter("state") == "DS_TIPO eq 'Estado'"


def test_tipo_filter_maps_municipality_synonyms_accent_insensitive():
    muni = "DS_TIPO eq 'Município'"
    assert _siope_tipo_filter("municipio") == muni
    assert _siope_tipo_filter("Município") == muni
    assert _siope_tipo_filter("municipios") == muni
    assert _siope_tipo_filter("municipality") == muni
    assert _siope_tipo_filter("municipalities") == muni


def test_tipo_filter_none_returns_filter_unchanged():
    assert _siope_tipo_filter(None) is None
    assert _siope_tipo_filter(None, "NOM_MUNI eq 'Recife'") == "NOM_MUNI eq 'Recife'"


def test_tipo_filter_combines_with_existing_filter():
    assert (
        _siope_tipo_filter("estado", "NUM_POPU gt 100000")
        == "(NUM_POPU gt 100000) and DS_TIPO eq 'Estado'"
    )


def test_tipo_filter_invalid_raises():
    with pytest.raises(ValueError, match="tipo"):
        _siope_tipo_filter("foobar")


@responses.activate
def test_siope_dados_gerais_sends_ds_tipo_filter():
    responses.add(
        responses.GET,
        _core.SIOPE_BASE_URL + "/Dados_Gerais_Siope(Ano_Consulta=@Ano_Consulta,"
        "Num_Peri=@Num_Peri,Sig_UF=@Sig_UF)",
        json={"value": [{"NOM_MUNI": "Recife"}]},
    )
    tesouropy.get_siope_dados_gerais(ano=2023, periodo=6, uf="PE", tipo="estado")
    qs = responses.calls[-1].request.url
    assert "DS_TIPO" in qs
    assert "Estado" in qs


@responses.activate
def test_siope_general_data_forwards_type_to_tipo():
    responses.add(
        responses.GET,
        _core.SIOPE_BASE_URL + "/Dados_Gerais_Siope(Ano_Consulta=@Ano_Consulta,"
        "Num_Peri=@Num_Peri,Sig_UF=@Sig_UF)",
        json={"value": [{"NOM_MUNI": "Recife"}]},
    )
    tesouropy.get_siope_general_data(
        year=2023, period=6, state="PE", type="municipality"
    )
    assert "DS_TIPO" in responses.calls[-1].request.url
