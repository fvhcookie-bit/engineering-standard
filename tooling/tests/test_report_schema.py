"""Структурная валидация отчёта schema:1."""

from core.gate_api import Finding, GateResult, Status
from core.report import build_report, validate_report


def _good() -> dict:
    result = GateResult(
        gate_id="DEMO-01", gate_version="1.0.0", status=Status.OK,
        findings=[Finding(code="X", severity="warning", path="a", line=1, message="m")],
    )
    return build_report(result)


def test_valid_report_has_no_errors():
    assert validate_report(_good()) == []


def test_missing_top_key():
    r = _good()
    del r["gate"]
    assert any("gate" in e for e in validate_report(r))


def test_bad_status():
    r = _good()
    r["status"] = "MAYBE"
    assert any("status" in e for e in validate_report(r))


def test_skip_requires_reason():
    r = _good()
    r["status"] = "SKIP"
    r["reason"] = ""
    assert any("reason" in e for e in validate_report(r))
    r["reason"] = "нет списка файлов задачи"
    assert validate_report(r) == []


def test_bad_severity_and_line():
    r = _good()
    r["findings"][0]["severity"] = "fatal"
    r["findings"][0]["line"] = -1
    errors = validate_report(r)
    assert len(errors) == 2
