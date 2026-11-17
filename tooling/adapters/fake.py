"""Offline-адаптер для тестов и демо: записывает вызовы, ничего не отправляет."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FakeAdapter:
    """calls — упорядоченный журнал ('method', аргументы) для ассертов тестов."""

    labels: dict[int, list[str]] = field(default_factory=dict)
    summaries: dict[int, list[str]] = field(default_factory=dict)
    reviews: dict[int, list[str]] = field(default_factory=dict)
    calls: list[tuple[str, ...]] = field(default_factory=list)

    def set_labels(self, pr_number: int, labels: list[str]) -> None:
        self.labels[pr_number] = list(labels)
        self.calls.append(("set_labels", str(pr_number), ",".join(labels)))

    def post_summary(self, pr_number: int, text_markdown: str) -> None:
        self.summaries.setdefault(pr_number, []).append(text_markdown)
        self.calls.append(("post_summary", str(pr_number), text_markdown[:40]))

    def list_review_logins(self, pr_number: int) -> list[str]:
        self.calls.append(("list_review_logins", str(pr_number)))
        return list(self.reviews.get(pr_number, []))
