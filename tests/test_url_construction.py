"""Tests that each API builds the expected URL and query parameters."""

import responses

import tesouropy
from tesouropy import _core


def _last_request():
    return responses.calls[-1].request


@responses.activate
def test_rreo_omits_none_co_esfera():
    url = _core.SICONFI_BASE_URL + "/rreo"
    responses.add(responses.GET, url, json={"items": [{"v": 1}], "hasMore": False})
    tesouropy.get_rreo_ufs(
        an_exercicio=2022, nr_periodo=6, co_tipo_demonstrativo="RREO",
        no_anexo="RREO-Anexo 01", id_ente=17,
    )
    qs = _last_request().url
    assert "an_exercicio=2022" in qs
    assert "id_ente=17" in qs
    assert "co_esfera" not in qs  # None must be dropped


@responses.activate
def test_budget_report_alias_maps_params():
    url = _core.SICONFI_BASE_URL + "/rreo"
    responses.add(responses.GET, url, json={"items": [{"v": 1}], "hasMore": False})
    tesouropy.get_budget_report_ufs(
        fiscal_year=2022, period=6, report_type="RREO",
        appendix="RREO-Anexo 01", entity_id=17, sphere="E",
    )
    qs = _last_request().url
    assert "co_tipo_demonstrativo=RREO" in qs
    assert "co_esfera=E" in qs
    assert "id_ente=17" in qs


@responses.activate
def test_deprecated_get_rreo_warns_and_forwards():
    import pytest

    url = _core.SICONFI_BASE_URL + "/rreo"
    responses.add(responses.GET, url, json={"items": [{"v": 1}], "hasMore": False})
    with pytest.warns(DeprecationWarning, match="get_rreo_ufs"):
        tesouropy.get_rreo(
            an_exercicio=2022, nr_periodo=6, co_tipo_demonstrativo="RREO",
            no_anexo="RREO-Anexo 01", id_ente=17,
        )
    assert "an_exercicio=2022" in _last_request().url


@responses.activate
def test_custos_pads_org_codes():
    url = _core.CUSTOS_BASE_URL + "/pessoal_ativo"
    responses.add(responses.GET, url, json={"items": [{"v": 1}], "hasMore": False})
    tesouropy.get_custos_pessoal_ativo(ano=2023, organizacao_n1=244,
                                       organizacao_n2=249)
    qs = _last_request().url
    assert "organizacao_n1=000244" in qs
    assert "organizacao_n2=000249" in qs


@responses.activate
def test_transferencias_municipio_uses_uppercase_params():
    url = _core.TRANSFERENCIAS_BASE_URL + "/por_estado_municipio"
    responses.add(responses.GET, url, json={"registros": [{"v": 1}]})
    tesouropy.get_tc_por_municipio(p_estado=17, p_municipio=[1, 2], p_ano=2023)
    qs = _last_request().url
    assert "P_ESTADO=17" in qs
    assert "P_MUNICIPIOS=1%3A2" in qs or "P_MUNICIPIOS=1:2" in qs
    assert "P_ANO=2023" in qs


@responses.activate
def test_transferencias_registros_key_parsed():
    url = _core.TRANSFERENCIAS_BASE_URL + "/estados"
    responses.add(
        responses.GET, url,
        json={"registros": [{"codigo": 1, "nome": "Acre"}]},
    )
    df = tesouropy.get_tc_estados()
    assert df.height == 1
    assert df["nome"].to_list() == ["Acre"]


@responses.activate
def test_siope_builds_odata_url_with_filter():
    # The OData segment contains parentheses; match by URL prefix.
    responses.add(
        responses.GET,
        _core.SIOPE_BASE_URL + "/Dados_Gerais_Siope(Ano_Consulta=@Ano_Consulta,"
        "Num_Peri=@Num_Peri,Sig_UF=@Sig_UF)",
        json={"value": [{"NOM_MUNI": "Recife", "NUM_POPU": "1600000"}]},
    )
    df = tesouropy.get_siope_dados_gerais(
        ano=2023, periodo=6, uf="PE", filter="NOM_MUNI eq 'Recife'",
    )
    assert df.height == 1
    qs = responses.calls[-1].request.url
    assert "%24filter" in qs or "$filter" in qs
    assert "%24format=json" in qs or "$format=json" in qs
    # numeric-looking string column should have been coerced to float
    assert df["num_popu"].dtype == _core.pl.Float64
