"""Q-19 «Аудит исключений и классов проектов» (ночной L4-гейт, TASK §3.2).

Целое дерево, не диф. Детерминизм: дата подаётся в конфиге (`today`), не берётся
из системы. Автозадача E-D — заглушка-событие в отчёте (реальный трекер — при
подключении адаптера, помечено в README гейта).
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from core.files import glob_matches
from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "Q-19"
GATE_VERSION = "1.0.0"

EX_ANCHOR = re.compile(r"EX-\d{4}-\d{3}")


class Q19AuditGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        today_raw = config.get("today")
        today = date.fromisoformat(str(today_raw)) if today_raw else date.today()
        k3_limit = float(config.get("k3_limit", 0.20))
        k3_alert = float(config.get("k3_alert", 0.16))

        entries = {e.id: e for e in inputs.registries.exceptions}

        # (1) якоря в коде <-> реестр
        anchored: dict[str, list[str]] = {}
        for rel in inputs.files.list_files():
            text = inputs.files.read(rel)
            if not text:
                continue
            for m in EX_ANCHOR.finditer(text):
                ex_id = m.group(0)
                anchored.setdefault(ex_id, []).append(rel)
                if ex_id not in entries:
                    result.findings.append(Finding(
                        code="ANCHOR_WITHOUT_ENTRY", severity="error",
                        path=rel, line=0,
                        message=f"якорь {ex_id} отсутствует в EXCEPTIONS.md",
                    ))

        # (2) просроченные сроки пересмотра — по затронутым файлам
        # (3) группировка по (принцип, причина)
        grouped: dict[tuple[str, str], list[str]] = {}
        for ex_id, entry in entries.items():
            files = anchored.get(ex_id, [])
            if not files:
                result.findings.append(Finding(
                    code="ENTRY_WITHOUT_ANCHOR", severity="error",
                    path="EXCEPTIONS.md", line=0,
                    message=f"запись {ex_id} без якоря в коде",
                ))
            if entry.review_due is not None and entry.review_due < today:
                target = files[0] if files else "EXCEPTIONS.md"
                result.findings.append(Finding(
                    code="EXPIRED_EXCEPTION", severity="error",
                    path=target, line=0,
                    message=f"исключение {ex_id} просрочено (до {entry.review_due})",
                ))
            key = (entry.principle, entry.reason)
            grouped.setdefault(key, []).append(ex_id)

        for (principle, reason), ids in sorted(grouped.items()):
            if len(ids) >= 3:
                result.findings.append(Finding(
                    code="AUTO_TASK_ED", severity="info",
                    path="EXCEPTIONS.md", line=0,
                    message=(f"{len(ids)} исключений принципа {principle} с одной причиной — "
                             "автозадача: PR в стандарт (E-D)"),
                    evidence=", ".join(sorted(ids)),
                ))

        # (4) доля К3-кода против лимитов (§0.6 EP, v1.2)
        k3_globs = [
            g.strip()
            for g in inputs.registries.repo_class.get("k3_globs", "").split(",")
            if g.strip()
        ]
        if k3_globs:
            all_files = inputs.files.list_files()
            k3_count = sum(
                1 for rel in all_files
                if any(glob_matches(rel, g) for g in k3_globs)
            )
            share = k3_count / len(all_files) if all_files else 0.0
            result.stats["k3_share"] = round(share, 4)
            result.stats["k3_limit"] = k3_limit
            if share > k3_limit:
                result.findings.append(Finding(
                    code="K3_LIMIT_EXCEEDED", severity="error",
                    path="REPO_CLASS", line=0,
                    message=f"доля К3-кода {share:.2%} выше лимита {k3_limit:.0%}",
                ))
            elif share >= k3_alert:
                result.findings.append(Finding(
                    code="K3_LIMIT_ALERT", severity="warning",
                    path="REPO_CLASS", line=0,
                    message=(f"доля К3-кода {share:.2%} приближается к лимиту "
                             f"{k3_limit:.0%} — алерт владельцу стандарта"),
                ))

        return result.finalize()
