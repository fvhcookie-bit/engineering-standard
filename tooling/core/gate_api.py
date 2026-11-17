"""Контракт гейта и общие типы (GUIDELINE_development §1, §3).

Каждый гейт — чистая функция над явными входами:
    run(GateInputs, GateConfig) -> GateResult
Никакого скрытого чтения окружения внутри гейта — всё через GateInputs
(тестируемость + запрет самоотчётности структурно, не дисциплинарно).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from core.diff import FileDiff
from core.files import RepoFiles
from core.registries import Registries


class Status(str, Enum):
    """Исходы гейта (TASK_guard-gates §4.2, GUIDELINE_development §5)."""

    OK = "OK"
    FAIL = "FAIL"
    SKIP = "SKIP"
    UNAVAILABLE = "UNAVAILABLE"


SEVERITIES = ("error", "warning", "info")


@dataclass(frozen=True)
class Finding:
    """Стабильный код + позиция + сообщение. Потребители опираются на `code`."""

    code: str
    severity: str  # error | warning | info
    path: str
    line: int
    message: str
    evidence: str = ""


@dataclass
class GateResult:
    gate_id: str
    gate_version: str
    status: Status
    reason: str = ""
    findings: list[Finding] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    second_reviewer_required: bool = False
    stats: dict[str, Any] = field(default_factory=dict)

    def finalize(self) -> GateResult:
        """Агрегация по правилам контракта: любой error -> FAIL; сортировка findings."""
        if any(f.severity == "error" for f in self.findings) and self.status is Status.OK:
            self.status = Status.FAIL
        self.findings.sort(key=lambda f: (f.path, f.line, f.code))
        self.labels = sorted(set(self.labels))
        return self


@dataclass
class GateInputs:
    """Явные входы гейта. Всё, что нужно гейту, подаётся сюда — и только это."""

    diff: list[FileDiff]  # результат core.diff.parse_unified_diff
    files: RepoFiles
    registries: Registries
    api: Any  # adapters.base.Adapter (Protocol); Any из-за типового цикла адаптеров
    pr_text: str = ""  # текст PR — ТОЛЬКО объект проверки (Q-15), не источник фактов
    commit_sha: str = ""  # SHA проверяемого коммита (Q-15 сверяет прогоны CI)


class Gate(Protocol):
    """Интерфейс гейта. Реализации — в gates/<id>/."""

    id: str
    version: str

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        ...
