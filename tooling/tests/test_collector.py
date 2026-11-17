"""D-1/D-2: сборщик дашборда и команда report collect (агрегаты, fail-closed)."""

import json
from datetime import date
from pathlib import Path

from collector import collect_dashboard, collect_reports, render_markdown
from runner.cli import main

TODAY = date(2026, 11, 18)

EXC_MD = """# Реестр исключений E-C

### EX-2026-001
- **Принцип:** B6
- **Суть отступления:** лимит задан протоколом
- **Срок пересмотра:** 2099-01-01
- **Статус:** активное

### EX-2026-002
- **Принцип:** C1
- **Суть отступления:** тест пропущен
- **Срок пересмотра:** 2026-01-31
- **Статус:** активное
"""


def _report(gate: str = "Q-11", findings: list | None = None,
            labels: list | None = None, stats: dict | None = None) -> dict:
    return {"schema": 1, "gate": gate, "gate_version": "1.0.0", "status": "OK",
            "reason": None, "findings": findings or [], "labels": labels or [],
            "second_reviewer_required": False, "stats": stats or {}}


def _write_pair(d: Path, name: str, report: dict, meta: dict | None = None) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.report.json").write_text(
        json.dumps(report, ensure_ascii=False), encoding="utf-8", newline="\n")
    if meta is not None:
        (d / f"{name}.meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8", newline="\n")


def test_collect_reports_pairs_and_tolerates_missing_meta(tmp_path):
    _write_pair(tmp_path, "r1", _report(), {"author": "alice"})
    (tmp_path / "r2.report.json").write_text(
        json.dumps(_report()), encoding="utf-8", newline="\n")
    pairs = collect_reports(tmp_path)
    assert len(pairs) == 2
    assert pairs[0][1].get("author") == "alice"
    assert pairs[1][1] == {}


def test_aggregation_by_author(tmp_path):
    _write_pair(tmp_path, "a1", _report(findings=[{"severity": "error"}],
               labels=["breaking"], stats={"suppressions_new": 3}),
               {"author": "alice", "pr": 7})
    _write_pair(tmp_path, "a2", _report(), {"author": "alice", "pr": 7})
    _write_pair(tmp_path, "b1", _report(gate="Q-19"), {"author": "bob"})
    dash = collect_dashboard(tmp_path, today=TODAY)
    by = {s["author"]: s for s in dash["subjects"]}
    assert by["alice"]["reports"] == 2
    assert by["alice"]["prs"] == 1
    assert by["alice"]["findings_error"] == 1
    assert by["alice"]["labels"] == {"breaking": 1}
    assert by["alice"]["gates"] == {"Q-11": 2}
    assert by["alice"]["suppressions_new"] == 3
    assert by["bob"]["reports"] == 1
    assert by["bob"]["prs"] == 0


def test_exceptions_active_expired_by_principle(tmp_path):
    dash = collect_dashboard(tmp_path, exceptions_text=EXC_MD, today=TODAY)
    exc = dash["exceptions"]
    assert exc["total"] == 2
    assert exc["active"] == 2
    assert exc["expired"] == 1
    assert exc["expired_ids"] == ["EX-2026-002"]
    assert exc["by_principle"] == {"B6": 1, "C1": 1}


def _baseline(generated_at: str) -> str:
    return f"schema: 1\ngenerated_at: '{generated_at}'\n"


def test_baseline_fresh_no_alert(tmp_path):
    bl = collect_dashboard(tmp_path, baseline_text=_baseline("2026-11-01"),
                           today=TODAY, stale_days=90)["baseline"]
    assert bl["age_days"] == 17
    assert bl["stale_alert"] is False


def test_baseline_stale_alert(tmp_path):
    bl = collect_dashboard(tmp_path, baseline_text=_baseline("2026-08-01"),
                           today=TODAY, stale_days=90)["baseline"]
    assert bl["stale_alert"] is True


def test_baseline_missing_generated_at_alerts(tmp_path):
    bl = collect_dashboard(tmp_path, baseline_text="schema: 1\n",
                           today=TODAY)["baseline"]
    assert bl["stale_alert"] is True
    assert "generated_at" in bl.get("reason", "")


def test_baseline_unparseable_generated_at_alerts(tmp_path):
    bl = collect_dashboard(tmp_path, baseline_text=_baseline("not-a-date"),
                           today=TODAY)["baseline"]
    assert bl["stale_alert"] is True


def test_markdown_renders_table_and_alerts(tmp_path):
    _write_pair(tmp_path, "r1", _report(), {"author": "alice", "pr": 7})
    dash = collect_dashboard(tmp_path, exceptions_text=EXC_MD,
                             baseline_text=_baseline("2026-08-01"),
                             today=TODAY, stale_days=90)
    md = render_markdown(dash)
    assert "| alice | 1 | 1 |" in md
    assert "Активных: 2; просроченных: 1." in md
    assert "ЗАСТОЙ" in md
    assert "- B6: 1" in md


def test_dashboard_is_deterministic(tmp_path):
    _write_pair(tmp_path, "r1", _report(), {"author": "alice", "pr": 7})
    kwargs: dict = {"exceptions_text": EXC_MD, "baseline_text": _baseline("2026-08-01"),
                    "today": TODAY, "stale_days": 90}
    first = collect_dashboard(tmp_path, **kwargs)
    second = collect_dashboard(tmp_path, **kwargs)
    assert json.dumps(first, ensure_ascii=False, sort_keys=True) == \
        json.dumps(second, ensure_ascii=False, sort_keys=True)


def test_report_collect_cli_writes_dashboard(tmp_path):
    d = tmp_path / "reps"
    _write_pair(d, "r1", _report(), {"author": "alice", "pr": 7})
    exc = tmp_path / "EXCEPTIONS.md"
    exc.write_text(EXC_MD, encoding="utf-8", newline="\n")
    base = tmp_path / "suppressions.yaml"
    base.write_text(_baseline("2026-11-01"), encoding="utf-8", newline="\n")
    out = tmp_path / "out"
    code = main(["report", "collect", "--reports-dir", str(d), "--out-dir", str(out),
                 "--exceptions", str(exc), "--baseline", str(base),
                 "--today", "2026-11-18", "--stale-days", "90"])
    assert code == 0
    dash = json.loads((out / "dashboard.json").read_text(encoding="utf-8"))
    assert dash["schema"] == 1
    assert dash["subjects"][0]["author"] == "alice"
    md = (out / "dashboard.md").read_text(encoding="utf-8")
    assert "Ок: возраст 17 д." in md


def test_report_collect_missing_reports_dir_exit_2(tmp_path):
    code = main(["report", "collect", "--reports-dir", str(tmp_path / "nope"),
                 "--out-dir", str(tmp_path / "out")])
    assert code == 2


def test_report_collect_missing_baseline_exit_2(tmp_path):
    d = tmp_path / "reps"
    d.mkdir()
    code = main(["report", "collect", "--reports-dir", str(d),
                 "--out-dir", str(tmp_path / "out"),
                 "--baseline", str(tmp_path / "no.yaml")])
    assert code == 2


DEMO_PATCH = (
    "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n"
    "@@ -1 +1,2 @@\n line\n+clean\n"
)


def test_run_writes_meta_and_collector_reads_it(tmp_path):
    patch = tmp_path / "d.patch"
    patch.write_text(DEMO_PATCH, encoding="utf-8", newline="\n")
    out = tmp_path / "runs" / "q11.report.json"
    code = main(["run", "--gate", "demo_dummy", "--diff", str(patch),
                 "--out", str(out), "--author", "alice", "--pr", "7"])
    assert code == 0
    meta = json.loads((tmp_path / "runs" / "q11.meta.json").read_text(encoding="utf-8"))
    assert meta == {"author": "alice", "pr": 7}
    dash = collect_dashboard(tmp_path / "runs", today=TODAY)
    alice = [s for s in dash["subjects"] if s["author"] == "alice"]
    assert len(alice) == 1
    assert alice[0]["prs"] == 1


def test_run_without_meta_flags_writes_no_meta(tmp_path):
    patch = tmp_path / "d.patch"
    patch.write_text(DEMO_PATCH, encoding="utf-8", newline="\n")
    out = tmp_path / "runs" / "q11.report.json"
    code = main(["run", "--gate", "demo_dummy", "--diff", str(patch), "--out", str(out)])
    assert code == 0
    assert not (tmp_path / "runs" / "q11.meta.json").exists()


def test_exception_status_variants(tmp_path):
    md = (
        "# Реестр исключений E-C\n\n"
        "### EX-2026-001\n"
        "- **Принцип:** B6\n"
        "- **Срок пересмотра:** 2099-01-01\n"
        "- **Статус:** Активное\n\n"
        "### EX-2026-002\n"
        "- **Принцип:** C1\n"
        "- **Срок пересмотра:** 2026-01-31\n"
        "- **Статус:** активное (продлено)\n\n"
        "### EX-2026-003\n- **Принцип:** C2\n- **Статус:** закрыто\n\n"
        "### EX-2026-004\n- **Принцип:** C3\n- **Статус:** приостановлено\n"
    )
    exc = collect_dashboard(tmp_path, exceptions_text=md, today=TODAY)["exceptions"]
    assert exc["total"] == 4
    assert exc["active"] == 2
    assert exc["expired_ids"] == ["EX-2026-002"]
    assert exc["by_principle"] == {"B6": 1, "C1": 1}
