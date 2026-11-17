"""C-7: CLI-покрытие (baseline migrate, коды ошибок) и Б-24 (детерминизм всех гейтов)."""

from pathlib import Path

from runner.cli import main
from tests.harness import make_diff

TOOLING = Path(__file__).resolve().parents[1]


def test_baseline_migrate_cli(tmp_path):
    base = {"src/legacy/app.py": "# noqa: E501\n" * 6}
    head = {"src/legacy/app2.py": "# noqa: E501\n" * 6}
    baseline = tmp_path / "suppressions.yaml"
    baseline.write_text(
        "schema: 1\ncounts:\n  noqa:\n    src/legacy/**: 6\n"
        "fingerprint: {}\ngenerated_by: init\n",
        encoding="utf-8", newline="\n")
    diff = tmp_path / "renames.patch"
    diff.write_text(make_diff(base, head), encoding="utf-8", newline="\n")
    head_root = tmp_path / "head"
    head_root.mkdir()
    for rel, content in head.items():
        p = head_root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")

    code = main(["baseline", "migrate", "--baseline", str(baseline),
                 "--diff", str(diff), "--repo-root", str(head_root),
                 "--dictionary", str(TOOLING / "dictionaries" / "python.yaml")])
    assert code == 0
    import yaml

    migrated = yaml.safe_load(baseline.read_text(encoding="utf-8"))
    assert migrated["counts"]["noqa"] == {"src/legacy/**": 6}


def test_baseline_migrate_config_error(tmp_path):
    code = main(["baseline", "migrate", "--baseline", str(tmp_path / "no.yaml"),
                 "--diff", str(tmp_path / "no.patch"), "--repo-root", str(tmp_path),
                 "--dictionary", "no.yaml"])
    assert code == 2


def test_q19_requires_repo_root():
    assert main(["run", "--gate", "q19_audit"]) == 2


def test_github_and_gitlab_adapter_branches(tmp_path):
    patch = tmp_path / "clean.patch"
    patch.write_text(
        "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1,2 @@\n line\n+clean\n",
        encoding="utf-8")
    assert main(["run", "--gate", "demo_dummy", "--diff", str(patch),
                 "--adapter", "github", "--repo", "octo/demo"]) == 0
    assert main(["run", "--gate", "demo_dummy", "--diff", str(patch),
                 "--adapter", "gitlab", "--project-id", "42"]) == 0


def test_b24_all_gates_deterministic(tmp_path):
    """Б-24: два прогона на одном входе — идентичные отчёты по байтам (все гейты)."""
    from adapters.fake import FakeAdapter
    from core.diff import parse_unified_diff
    from core.files import RepoFiles
    from core.gate_api import GateInputs, Registries
    from core.report import build_report, render_report
    from gates import GATES

    diff = parse_unified_diff(
        (TOOLING / "fixtures" / "demo_dummy" / "diff.patch").read_text(encoding="utf-8"))
    for name, gate in sorted(GATES.items()):
        def run_once() -> str:
            inputs = GateInputs(diff=diff, files=RepoFiles(root=None),
                                registries=Registries.empty(), api=FakeAdapter())
            config = {"patterns": []} if name == "q11_suppressions" else {}
            return render_report(build_report(gate.run(inputs, config=config)))

        first = run_once()
        assert first == run_once(), f"{name}: отчёты двух прогонов различаются"
        assert '"schema": 1' in first
