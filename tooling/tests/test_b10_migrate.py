"""Б-10: миграция baseline инструментом при rename (baseline migrate)."""

from pathlib import Path

from core.baseline import migrate
from core.dictionary import load_dictionary
from core.diff import parse_unified_diff
from core.files import RepoFiles
from core.registries import load_baseline

TOOLING = Path(__file__).resolve().parents[1]
FIXTURE = TOOLING / "fixtures" / "b_10"


def _tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
            for p in root.rglob("*") if p.is_file()}


def test_migrate_preserves_counts_on_rename(tmp_path):
    baseline = load_baseline((FIXTURE / "head" / "baseline" / "suppressions.yaml").read_text(encoding="utf-8"))
    assert baseline["counts"]["noqa"] == {"src/legacy/**": 6}

    head = _tree(FIXTURE / "head")
    del head["baseline/suppressions.yaml"]
    for rel, content in head.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")

    from tests.harness import make_diff

    base = _tree(FIXTURE / "base")
    diff_text = make_diff(base, head)
    diff_files = parse_unified_diff(diff_text)
    assert diff_files[0].is_rename is True

    patterns = load_dictionary((TOOLING / "dictionaries" / "python.yaml").read_text(encoding="utf-8"))
    new_baseline = migrate(baseline, RepoFiles(root=tmp_path), patterns, {}, diff_files)

    # счётчик сохранился; glob остался корректным (rename внутри каталога)
    assert new_baseline["counts"]["noqa"] == {"src/legacy/**": 6}
    assert new_baseline["schema"] == 1
