"""Тесты Q-10: breaking -> метка breaking; язык без инструмента -> UNAVAILABLE."""

from adapters.fake import FakeAdapter
from core.diff import parse_unified_diff
from core.files import RepoFiles
from core.gate_api import GateInputs, Registries
from core.report import build_report
from gates import get_gate

STUB_BREAKING = [
    "python", "-c",
    "import json,sys; print(json.dumps(["
    "{\"path\": \"src/api.py\", \"symbol\": \"get_user\", \"kind\": \"breaking\"}]))",
]
STUB_CLEAN = [
    "python", "-c",
    "import json,sys; print(json.dumps(["
    "{\"path\": \"src/api.py\", \"symbol\": \"get_user\", \"kind\": \"api-change\"}]))",
]


def _diff() -> str:
    return ("diff --git a/src/api.py b/src/api.py\n--- a/src/api.py\n+++ b/src/api.py\n"
            "@@ -1 +1,2 @@\n def get_user(): ...\n+def get_admin(): ...\n")


def _run(config: dict):
    gate = get_gate("q10_api_diff")
    inputs = GateInputs(
        diff=parse_unified_diff(_diff()), files=RepoFiles(root=None),
        registries=Registries.empty(), api=FakeAdapter(),
    )
    return gate.run(inputs, config=config)


def test_b21_breaking_found_sets_label():
    result = _run({"tools": [{"language": "python", "cmd": STUB_BREAKING}],
                   "base": "main", "head": "HEAD"})
    assert result.status.value == "FAIL"
    assert "breaking" in result.labels
    assert "api-change" in result.labels
    assert "API_BREAKING" in {f.code for f in result.findings}


def test_clean_api_change_only():
    result = _run({"tools": [{"language": "python", "cmd": STUB_CLEAN}],
                   "base": "main", "head": "HEAD"})
    assert result.status.value == "OK"
    assert "api-change" in result.labels
    assert "breaking" not in result.labels


def test_missing_tool_is_unavailable_not_silent_ok():
    result = _run({"tools": [], "base": "main", "head": "HEAD"})
    assert result.status.value == "UNAVAILABLE"
    assert "python" in result.reason


def test_tool_failure_is_unavailable(tmp_path):
    broken = [sys_exec(), "-c", "import sys; sys.exit(3)"]
    result = _run({"tools": [{"language": "python", "cmd": broken}],
                   "base": "main", "head": "HEAD"})
    assert result.status.value == "UNAVAILABLE"


def test_report_is_deterministic():
    a = build_report(_run({"tools": [{"language": "python", "cmd": STUB_CLEAN}],
                           "base": "main", "head": "HEAD"}))
    b = build_report(_run({"tools": [{"language": "python", "cmd": STUB_CLEAN}],
                           "base": "main", "head": "HEAD"}))
    assert a == b


def sys_exec() -> str:
    import sys

    return sys.executable
