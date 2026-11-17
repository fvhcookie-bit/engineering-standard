"""Полный цикл демо-гейта (M1): fixture -> отчёт по байтам -> метка адаптером."""

import json
from pathlib import Path

from adapters.fake import FakeAdapter
from core.diff import parse_unified_diff
from core.files import RepoFiles
from core.gate_api import GateInputs
from core.registries import Registries
from core.report import build_report, render_report, validate_report
from gates import get_gate

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "demo_dummy"


def _run_once() -> tuple[FakeAdapter, str]:
    gate = get_gate("demo_dummy")
    api = FakeAdapter()
    inputs = GateInputs(
        diff=parse_unified_diff((FIXTURE / "diff.patch").read_text(encoding="utf-8")),
        files=RepoFiles(root=None),
        registries=Registries.empty(),
        api=api,
    )
    result = gate.run(inputs, config={})
    report = build_report(result)
    errors = validate_report(report)
    assert errors == [], errors
    assert api.calls == []  # runner отправляет метки после прогона, не гейт
    return api, render_report(report)


def test_report_matches_expected_bytes():
    _, text = _run_once()
    expected = (FIXTURE / "expected.json").read_text(encoding="utf-8")
    assert text == expected


def test_determinism_two_runs_byte_identical():
    _, first = _run_once()
    _, second = _run_once()
    assert first == second


def test_labels_set_by_runner_after_full_run():
    api, _ = _run_once()
    gate_out = json.loads((FIXTURE / "expected.json").read_text(encoding="utf-8"))
    api.set_labels(pr_number=7, labels=gate_out["labels"])
    assert api.labels[7] == ["demo-label"]
    assert ("set_labels", "7", "demo-label") in api.calls


def test_clean_diff_is_ok():
    clean = parse_unified_diff(
        "diff --git a/x.py b/x.py\n"
        "--- a/x.py\n+++ b/x.py\n"
        "@@ -1 +1,2 @@\n"
        " line\n"
        "+clean\n"
    )
    gate = get_gate("demo_dummy")
    result = gate.run(
        GateInputs(diff=clean, files=RepoFiles(root=None),
                   registries=Registries.empty(), api=FakeAdapter()),
        config={},
    )
    assert result.status.value == "OK"
    assert result.findings == []
    assert result.labels == []
