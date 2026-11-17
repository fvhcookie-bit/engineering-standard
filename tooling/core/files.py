"""Безопасная работа с файлами целевого репозитория (GUIDELINE_development §6).

Код целевого репозитория не исполняется; содержимое — данные. Пути нормализуются,
выход за корень (symlink-escape) запрещён; слишком большие файлы пропускаются.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_MAX_FILE_BYTES = 5 * 1024 * 1024  # > 5 МБ — пропуск с info (гайдлайн §6.3)


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
