"""Профили стеков: конфиги разбираются своим форматом и содержат строгие маркеры."""

import configparser
import json
import tomllib
from pathlib import Path

import yaml

PROFILES = Path(__file__).resolve().parents[1] / "profiles"


def test_python_ruff_toml_parses_and_strict():
    data = tomllib.loads((PROFILES / "python" / "ruff.toml").read_text(encoding="utf-8"))
    assert data["lint"]["select"] == ["ALL"]
    assert data["lint"]["mccabe"]["max-complexity"] <= 10  # A4-триггер


def test_python_mypy_strict():
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string((PROFILES / "python" / "mypy.ini").read_text(encoding="utf-8"))
    assert parser["mypy"]["strict"].lower() == "true"


def test_typescript_configs_parse_and_strict():
    ts = json.loads((PROFILES / "typescript" / "tsconfig.strict.json").read_text(encoding="utf-8"))
    assert ts["compilerOptions"]["strict"] is True
    assert ts["compilerOptions"]["noUncheckedIndexedAccess"] is True
    eslint = json.loads((PROFILES / "typescript" / "eslint.config.json").read_text(encoding="utf-8"))
    assert eslint["rules"]["no-explicit-any"] == "error"


def test_go_golangci_yaml_parses_and_strict():
    data = yaml.safe_load((PROFILES / "go" / "golangci-lint.yml").read_text(encoding="utf-8"))
    assert "errcheck" in data["linters"]["enable"]  # D3
    assert data["linters-settings"]["gocyclo"]["min-complexity"] <= 10


def test_rust_clippy_deny_warnings():
    data = tomllib.loads((PROFILES / "rust" / "clippy-lints.toml").read_text(encoding="utf-8"))
    clippy = data["lints"]["clippy"]
    assert clippy["all"]["level"] == "deny"


def test_clang_tidy_yaml_strict():
    data = yaml.safe_load((PROFILES / "c-cpp" / ".clang-tidy").read_text(encoding="utf-8"))
    checks = data["Checks"]
    assert "bugprone-*" in checks
    assert "WarningsAsErrors" in data


def test_java_detekt_zero_issues():
    data = yaml.safe_load((PROFILES / "java" / "detekt.yml").read_text(encoding="utf-8"))
    assert data["build"]["maxIssues"] == 0
