"""Протокол адаптера хостинга. Реализации НЕ вызываются из гейтов напрямую —
только runner'ом после полного прогона (метки ставятся одним пакетом, §8)."""

from __future__ import annotations

from typing import Protocol


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
