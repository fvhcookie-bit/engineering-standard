"""CLI: коды выхода 0/1/2 и артефакт отчёта."""

from pathlib import Path

from runner.cli import main

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "demo_dummy"


def test_fail_exit_code_and_out_file(tmp_path):
    out = tmp_path / "report.json"
    code = main(["run", "--gate", "demo_dummy",
                 "--diff", str(FIXTURE / "diff.patch"), "--out", str(out)])
    assert code == 1
    assert out.read_text(encoding="utf-8") == (FIXTURE / "expected.json").read_text(encoding="utf-8")


def test_unknown_gate_is_config_error():
    assert main(["run", "--gate", "nope", "--diff", str(FIXTURE / "diff.patch")]) == 2


def test_missing_diff_is_config_error():
    assert main(["run", "--gate", "demo_dummy", "--diff", "nope.patch"]) == 2


def test_gates_listing(capsys):
    assert main(["gates"]) == 0
    assert "demo_dummy" in capsys.readouterr().out


def test_clean_diff_ok(tmp_path):
    patch = tmp_path / "clean.patch"
    patch.write_text(
        "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n"
        "@@ -1 +1,2 @@\n line\n+clean\n",
        encoding="utf-8",
    )
    assert main(["run", "--gate", "demo_dummy", "--diff", str(patch)]) == 0
