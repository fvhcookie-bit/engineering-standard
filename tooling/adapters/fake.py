"""Offline-адаптер для тестов и демо: записывает вызовы, ничего не отправляет."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapters.base import AdapterUnavailable


@dataclass
class FakeAdapter:
    """calls — упорядоченный журнал ('method', аргументы) для ассертов тестов."""

    labels: dict[int, list[str]] = field(default_factory=dict)
    summaries: dict[int, list[str]] = field(default_factory=dict)
    reviews: dict[int, list[str]] = field(default_factory=dict)
    branch_protection: dict[str, Any] | None = None  # None = ветка не защищена
    protection_unavailable: str | None = None  # причина недоступности (fail-closed)
    codeowners: str | None = None
    commit_status: str | None = "success"
    run_ownership: dict[int, bool] = field(default_factory=dict)
    task_files: dict[str, list[str] | None] = field(default_factory=dict)
    tracker_unavailable: str | None = None
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

    def get_branch_protection(self, branch: str) -> dict[str, Any] | None:
        self.calls.append(("get_branch_protection", branch))
        if self.protection_unavailable:
            raise AdapterUnavailable(self.protection_unavailable)
        return self.branch_protection

    def get_codeowners(self) -> str | None:
        self.calls.append(("get_codeowners",))
        return self.codeowners

    def get_commit_check_status(self, commit_sha: str) -> str | None:
        self.calls.append(("get_commit_check_status", commit_sha))
        return self.commit_status

    def run_belongs_to_commit(self, run_id: int, commit_sha: str) -> bool:
        self.calls.append(("run_belongs_to_commit", str(run_id), commit_sha))
        return self.run_ownership.get(run_id, False)

    def get_task_files(self, task_id: str) -> list[str] | None:
        self.calls.append(("get_task_files", task_id))
        if self.tracker_unavailable:
            raise AdapterUnavailable(self.tracker_unavailable)
        return self.task_files.get(task_id)
