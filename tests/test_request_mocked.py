"""HTTP-level tests using the `responses` library to mock requests."""

import polars as pl
import pytest
import responses

import tesouropy
from tesouropy import _core
from tesouropy._core import TesouroError, tnr_request


@responses.activate
def test_tnr_request_success_and_cache():
    responses.add(
        responses.GET, "https://example.test/api",
        json={"items": [{"a": 1}]}, status=200,
    )
    body = tnr_request("https://example.test/api", {"x": 1})
    assert body == {"items": [{"a": 1}]}
    # second call must hit the cache, not the network
    body2 = tnr_request("https://example.test/api", {"x": 1})
    assert body2 == body
    assert len(responses.calls) == 1


@responses.activate
def test_tnr_request_retries_then_succeeds():
    responses.add(responses.GET, "https://example.test/r", status=503)
    responses.add(responses.GET, "https://example.test/r", status=503)
    responses.add(
        responses.GET, "https://example.test/r",
        json={"ok": True}, status=200,
    )
    body = tnr_request("https://example.test/r", use_cache=False)
    assert body == {"ok": True}
    assert len(responses.calls) == 3


@responses.activate
def test_tnr_request_non_retryable_404_raises():
    responses.add(responses.GET, "https://example.test/nf", status=404)
    with pytest.raises(TesouroError, match="HTTP status 404"):
        tnr_request("https://example.test/nf", use_cache=False)
    assert len(responses.calls) == 1  # 404 is not retried


@responses.activate
def test_tnr_request_400_includes_server_message():
    responses.add(
        responses.GET, "https://example.test/bad",
        json={"message": "invalid column FOO"}, status=400,
    )
    with pytest.raises(TesouroError, match="invalid column FOO"):
        tnr_request("https://example.test/bad", use_cache=False)


@responses.activate
def test_ords_pagination_follows_hasmore():
    base = _core.SICONFI_BASE_URL + "/entes"
    responses.add(
        responses.GET, base,
        json={"items": [{"id": 1}, {"id": 2}], "hasMore": True,
              "offset": 0, "limit": 2},
        status=200,
    )
    responses.add(
        responses.GET, base,
        json={"items": [{"id": 3}], "hasMore": False, "offset": 2, "limit": 2},
        status=200,
    )
    df = tesouropy.get_entes()
    assert df.height == 3
    assert df["id"].to_list() == [1, 2, 3]


@responses.activate
def test_ords_partial_on_midpagination_failure():
    base = _core.SICONFI_BASE_URL + "/entes"
    responses.add(
        responses.GET, base,
        json={"items": [{"id": 1}], "hasMore": True, "offset": 0, "limit": 1},
        status=200,
    )
    # every subsequent page fails with a non-retryable 404
    responses.add(responses.GET, base, status=404)
    df = tesouropy.get_entes()
    assert df.height == 1
    assert getattr(df, "partial", False) is True
    assert getattr(df, "last_page_error", None)


@responses.activate
def test_clean_names_applied_to_response():
    base = _core.SICONFI_BASE_URL + "/entes"
    responses.add(
        responses.GET, base,
        json={"items": [{"Cod IBGE": 17, "AN_EXERCICIO": 2022}],
              "hasMore": False},
        status=200,
    )
    df = tesouropy.get_entes()
    assert set(df.columns) == {"cod_ibge", "an_exercicio"}
