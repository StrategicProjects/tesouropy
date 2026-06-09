import pytest

import tesouropy
from tesouropy import _core


@pytest.fixture(autouse=True)
def _clear_cache():
    """Each test starts with an empty in-memory cache."""
    _core._CACHE.clear()
    yield
    _core._CACHE.clear()


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Never actually sleep during retry backoff in tests."""
    monkeypatch.setattr(_core, "_sleep", lambda seconds: None)
