"""Протокол адаптера хостинга. Реализации НЕ вызываются из гейтов напрямую —
только runner'ом после полного прогона (метки ставятся одним пакетом, §8)."""

from __future__ import annotations

from typing import Any, Protocol


class AdapterUnavailable(Exception):
    """Хостинг/CI недоступен или данных нет (fail-closed -> UNAVAILABLE)."""


class Adapter(Protocol):
    def set_labels(self, pr_number: int, labels: list[str]) -> None:
        """Полная замена набора guard-меток PR (одним вызовом, не частями)."""
        ...

    def post_summary(self, pr_number: int, text_markdown: str) -> None:
        """Человекочитаемая сводка отчёта (аннотации/комментарий)."""
        ...

    def list_review_logins(self, pr_number: int) -> list[str]:
        """Логины уже оставивших ревью (нужно L0/второму ревьюеру)."""
        ...

    def get_branch_protection(self, branch: str) -> dict[str, Any] | None:
        """Настройки защиты ветки; None — ветка не защищена (L0)."""
        ...

    def get_codeowners(self) -> str | None:
        """Текст CODEOWNERS; None — файла нет (L0)."""
        ...

    def get_commit_check_status(self, commit_sha: str) -> str | None:
        """Итог конвейера по коммиту: "success" | "failure" | None (нет данных)."""
        ...

    def run_belongs_to_commit(self, run_id: int, commit_sha: str) -> bool:
        """Прогон с таким id выполнялся на этом коммите (Б-16)."""
        ...

    def get_task_files(self, task_id: str) -> list[str] | None:
        """Список файлов задачи из трекера; None — список не заведён (Б-13)."""
        ...
