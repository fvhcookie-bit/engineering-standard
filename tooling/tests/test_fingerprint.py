"""Config-fingerprint: канонизация и чувствительность к порогам."""

from core.config_fingerprint import detect_tool, fingerprint


def test_detect_tool():
    assert detect_tool("sub/.eslintrc.json") == "eslint_json"
    assert detect_tool("pyproject.toml") == "ruff"
    assert detect_tool("src/.mypy.ini") == "mypy"
    assert detect_tool("src/app.py") is None


def test_fingerprint_stable_and_sensitive():
    a1 = fingerprint('[tool.ruff]\nselect = ["E"]\n', "ruff")
    a2 = fingerprint('[tool.ruff]\nselect = ["E"]\n', "ruff")
    b = fingerprint('[tool.ruff]\nselect = ["E", "W"]\n', "ruff")
    assert a1 == a2
    assert a1 != b
    assert a1.startswith("sha256:")


def test_fingerprint_canonical_orders_keys():
    a = fingerprint('{"rules": {"a": 1, "b": 2}}', "eslint_json")
    b = fingerprint('{"rules": {"b": 2, "a": 1}}', "eslint_json")
    assert a == b


def test_unparsable_config_returns_none():
    assert fingerprint("это не toml = (((", "ruff") is None
