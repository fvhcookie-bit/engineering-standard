"""Сборка и структурная валидация отчёта (схема schema:1 — TASK_guard-gates §4.6).

Детерминизм: build_report не содержит меток времени; render_report даёт
байт-стабильный вывод (порядок ключей фиксирован, findings отсортированы).
"""

from __future__ import annotations

import json
from typing import Any

from core.gate_api import SEVERITIES, GateResult, Status

SCHEMA_VERSION = 1
STATUS_VALUES = frozenset(s.value for s in Status)

_TOP_KEYS = ("schema", "gate", "gate_version", "status", "reason",
             "findings", "labels", "second_reviewer_required", "stats")
_FINDING_KEYS = ("code", "severity", "path", "line", "message", "evidence")


def build_report(result: GateResult) -> dict[str, Any]:
    """Отчёт гейта в схеме schema:1. Порядок ключей фиксирован."""
    return {
        "schema": SCHEMA_VERSION,
        "gate": result.gate_id,
        "gate_version": result.gate_version,
        "status": result.status.value,
        "reason": result.reason,
        "findings": [
            {
                "code": f.code,
                "severity": f.severity,
                "path": f.path,
                "line": f.line,
                "message": f.message,
                "evidence": f.evidence,
            }
            for f in result.findings
        ],
        "labels": list(result.labels),
        "second_reviewer_required": result.second_reviewer_required,
        "stats": result.stats,
    }


def render_report(report: dict[str, Any]) -> str:
    """Байт-стабильный текстовый рендер отчёта."""
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def validate_report(report: dict[str, Any]) -> list[str]:
    """Структурная валидация без внешних зависимостей. Пусто — отчёт корректен."""
    errors: list[str] = []
    for key in _TOP_KEYS:
        if key not in report:
            errors.append(f"нет ключа: {key}")
    if report.get("schema") != SCHEMA_VERSION:
        errors.append(f"schema != {SCHEMA_VERSION}")
    if report.get("status") not in STATUS_VALUES:
        errors.append(f"недопустимый status: {report.get('status')!r}")
    if report.get("status") in (Status.SKIP.value, Status.UNAVAILABLE.value) and not report.get("reason"):
        errors.append("SKIP/UNAVAILABLE требует reason")
    findings = report.get("findings")
    if not isinstance(findings, list):
        errors.append("findings не список")
        return errors
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"findings[{i}] не объект")
            continue
        for key in _FINDING_KEYS:
            if key not in f:
                errors.append(f"findings[{i}]: нет ключа {key}")
        if f.get("severity") not in SEVERITIES:
            errors.append(f"findings[{i}]: недопустимая severity {f.get('severity')!r}")
        if not isinstance(f.get("line"), int) or f.get("line", 0) < 0:
            errors.append(f"findings[{i}]: line должен быть int >= 0")
    labels = report.get("labels")
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        errors.append("labels не список строк")
    if not isinstance(report.get("stats"), dict):
        errors.append("stats не объект")
    return errors
