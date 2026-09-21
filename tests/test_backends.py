import pytest

from invoice_scanner import available, get_backend


def test_builtin_backends_registered():
    assert {"claude", "ollama"} <= set(available())


def test_get_backend_returns_callable():
    assert callable(get_backend("claude"))


def test_get_backend_with_model():
    assert callable(get_backend("ollama", model="qwen2.5vl"))


def test_unknown_backend_raises():
    with pytest.raises(ValueError, match="unknown backend"):
        get_backend("nope")
