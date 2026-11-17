"""Baseline подавлений: миграция инструментом (Б-10), никогда не руками.

Правила (GUIDELINE_profiles_and_dictionaries §1.3): рост любого счётчика -> FAIL;
baseline и код — разные PR; migrate пересчитывает счётчики по head с учётом
rename-карты из дифа механического PR.
"""

from __future__ import annotations

from typing import Any

from core.dictionary import Pattern, language_of
from core.diff import FileDiff
from core.files import RepoFiles, glob_matches


def rename_map(files: list[FileDiff]) -> dict[str, str]:
    return {f.old_path: f.path for f in files if f.is_rename and f.old_path}


def count_head_suppressions(
    root_files: RepoFiles, patterns: list[Pattern],
    ext_map: dict[str, list[str]] | None = None,
) -> dict[str, dict[str, int]]:
    """Фактические подавления в дереве head: kind -> путь -> число."""
    ext_map = ext_map or {"python": [".py"]}
    counts: dict[str, dict[str, int]] = {}
    for rel in root_files.list_files():
        lang = language_of(rel, ext_map)
        if lang is None:
            continue
        text = root_files.read(rel)
        if not text:
            continue
        for pat in patterns:
            if lang not in pat.languages:
                continue
            n = len(pat.regex.findall(text))
            if n:
                counts.setdefault(pat.id, {})[rel] = n
    return counts


def _apply_renames_to_glob(glob: str, renames: dict[str, str]) -> str:
    for old, new in renames.items():
        if glob_matches(old, glob):
            old_dir = "/".join(old.split("/")[:-1])
            new_dir = "/".join(new.split("/")[:-1])
            if old_dir and old_dir in glob:
                return glob.replace(old_dir, new_dir)
    return glob


def migrate(
    baseline: dict[str, Any],
    head_files: RepoFiles,
    patterns: list[Pattern],
    ext_map: dict[str, list[str]],
    diff_files: list[FileDiff],
) -> dict[str, Any]:
    """Новый baseline: тот же скелет, счётчики пересчитаны по head.

    Пересчёт выполняется только для globs, затронутых rename; остальные
    сохраняются без изменений (механический PR не должен ничего «починить»).
    """
    renames = rename_map(diff_files)
    counts = count_head_suppressions(head_files, patterns, ext_map)
    out: dict[str, Any] = {
        "schema": 1,
        "counts": {},
        "fingerprint": baseline.get("fingerprint", {}),
        "generated_by": "gate-runner baseline migrate",
    }
    for kind, globs in baseline.get("counts", {}).items():
        new_globs: dict[str, int] = {}
        for glob, maxv in globs.items():
            touched = any(glob_matches(old, glob) for old in renames)
            if touched:
                new_glob = _apply_renames_to_glob(glob, renames)
                total = sum(
                    n for path, n in counts.get(kind, {}).items()
                    if glob_matches(path, new_glob)
                )
                new_globs[new_glob] = total
            else:
                new_globs[glob] = maxv
        out["counts"][kind] = new_globs
    # появившиеся в head виды, которых не было в baseline, не добавляются молча:
    # их рост ловит гейт; добавление — через PR с changelog.
    return out
