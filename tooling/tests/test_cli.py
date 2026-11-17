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


CLEAN_PATCH = (
    "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n"
    "@@ -1 +1,2 @@\n line\n+clean\n"
)


def _clean(tmp_path):
    patch = tmp_path / "clean.patch"
    patch.write_text(CLEAN_PATCH, encoding="utf-8", newline="\n")
    return patch


def test_github_adapter_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/demo")
    assert main(["run", "--gate", "demo_dummy", "--diff", str(_clean(tmp_path)),
                 "--adapter", "github"]) == 0


def test_github_adapter_without_repo_is_config_error(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert main(["run", "--gate", "demo_dummy", "--diff", str(_clean(tmp_path)),
                 "--adapter", "github"]) == 2


def test_github_explicit_repo_overrides_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/env")
    assert main(["run", "--gate", "demo_dummy", "--diff", str(_clean(tmp_path)),
                 "--adapter", "github", "--repo", "octo/arg"]) == 0


def test_gitlab_adapter_env_and_config_error(tmp_path, monkeypatch):
    patch = _clean(tmp_path)
    monkeypatch.setenv("CI_PROJECT_ID", "42")
    assert main(["run", "--gate", "demo_dummy", "--diff", str(patch),
                 "--adapter", "gitlab"]) == 0
    monkeypatch.delenv("CI_PROJECT_ID", raising=False)
    assert main(["run", "--gate", "demo_dummy", "--diff", str(patch),
                 "--adapter", "gitlab"]) == 2
