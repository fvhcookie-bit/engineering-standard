"""Безопасная работа с файлами целевого репозитория (GUIDELINE_development §6).

Код целевого репозитория не исполняется; содержимое — данные. Пути нормализуются,
выход за корень (symlink-escape) запрещён; слишком большие файлы пропускаются.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

DEFAULT_MAX_FILE_BYTES = 5 * 1024 * 1024  # > 5 МБ — пропуск с info (гайдлайн §6.3)


def glob_matches(path: str, glob: str) -> bool:
    """fnmatch + поддержка '**/' как «ноль или больше каталогов»."""
    if fnmatch.fnmatch(path, glob):
        return True
    alt = glob
    while alt.startswith("**/"):
        alt = alt[3:]
        if fnmatch.fnmatch(path, alt):
            return True
    return False


class PathEscape(Exception):
    """Путь выходит за корень репозитория — потенциальный symlink/..-escape."""


class RepoFiles:
    """Чтение файлов целевого репозитория с защитой путей и лимитом размера."""

    def __init__(self, root: Path | None, max_file_bytes: int = DEFAULT_MAX_FILE_BYTES) -> None:
        self._root = root.resolve() if root is not None else None
        self._max = max_file_bytes

    def read(self, rel_path: str) -> str | None:
        """Текст файла внутри корня. None — файла нет или он слишком велик."""
        if self._root is None:
            return None
        target = (self._root / rel_path).resolve()
        if target != self._root and self._root not in target.parents:
            raise PathEscape(f"путь вне корня репозитория: {rel_path}")
        if not target.is_file():
            return None
        if target.stat().st_size > self._max:
            return None
        return target.read_text(encoding="utf-8", errors="replace")

    def list_files(self) -> list[str]:
        """Все файлы дерева (кроме .git), относительные пути, отсортированы."""
        if self._root is None:
            return []
        out: list[str] = []
        for p in self._root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(self._root).as_posix()
            if rel.startswith(".git/") or "/.git/" in "/" + rel:
                continue
            out.append(rel)
        return sorted(out)
