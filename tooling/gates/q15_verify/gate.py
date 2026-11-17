"""Q-15 «Верификация и статус CI» (TASK §3.4).

Текст PR — только объект проверки. Источник правды — статус конвейера (Adapter).
- утверждение успеха («тесты прошли») при красном конвейере — механический FAIL (Б-15);
- ссылка на прогон, не относящийся к коммиту — FAIL (Б-16);
- упомянутая команда верификации отсутствует в проекте — FAIL;
- не заполнено «стоп-события сессии» — предупреждение (процессное).
"""

from __future__ import annotations

import re
from typing import Any

from adapters.base import AdapterUnavailable
from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "Q-15"
GATE_VERSION = "1.0.0"

RUN_REF = re.compile(r"run/(\d+)|#run(\d+)\b")
CMD_LINE = re.compile(r"^\s*\$\s*(.+)$", re.M)


class Q15VerifyGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        pr_text = inputs.pr_text
        commit_sha = inputs.commit_sha
        markers = [m.lower() for m in config.get("success_markers",
                    ["тесты прошли", "tests pass", "сборка ок", "build ok"])]
        known_commands: list[str] = config.get("known_commands", [])
        stop_marker = str(config.get("stop_events_marker", "стоп-события"))

        # Источник правды — конвейер (fail-closed при недоступности)
        try:
            status = inputs.api.get_commit_check_status(commit_sha) if commit_sha else None
            run_refs = []
            for m in RUN_REF.finditer(pr_text):
                digits = m.group(1) or m.group(2)
                run_refs.append((int(digits), m.group(0)))
            ownership = {rid: inputs.api.run_belongs_to_commit(rid, commit_sha)
                         for rid, _ in run_refs}
        except AdapterUnavailable as exc:
            result.status = Status.UNAVAILABLE
            result.reason = f"статус конвейера недоступен: {exc}"
            return result.finalize()

        # (Б-15) заявление об успехе при красном конвейере
        if status == "failure":
            for marker in markers:
                if marker in pr_text.lower():
                    result.findings.append(Finding(
                        code="SUCCESS_MARKER_AT_RED", severity="error",
                        path="PR", line=0,
                        message=(f"заявлено «{marker}», но конвейер на этом коммите красный — "
                                 "источник статуса только CI"),
                    ))
                    break

        # (Б-16) ссылка на чужой/несуществующий прогон
        for rid, marker in run_refs:
            if not ownership.get(rid, False):
                result.findings.append(Finding(
                    code="UNKNOWN_RUN_REFERENCE", severity="error",
                    path="PR", line=0,
                    message=f"упомянутый прогон {marker} не относится к коммиту {commit_sha[:8]}",
                ))

        # упомянутые команды верификации должны существовать в проекте
        for m in CMD_LINE.finditer(pr_text):
            command = m.group(1).strip().split()
            if command and known_commands and command[0] not in known_commands:
                result.findings.append(Finding(
                    code="UNKNOWN_VERIFY_COMMAND", severity="error",
                    path="PR", line=0,
                    message=f"команда верификации «{command[0]}» отсутствует в конфигурации репозитория",
                ))

        # процессное: поле «стоп-события сессии» не заполнено
        if pr_text and stop_marker.lower() not in pr_text.lower():
            result.findings.append(Finding(
                code="STOP_EVENTS_MISSING", severity="warning",
                path="PR", line=0,
                message=f"не заполнено поле «{stop_marker}» (процессное требование Q-15)",
            ))

        result.stats = {"commit_status": status or "нет данных",
                        "run_references": len(run_refs)}
        return result.finalize()
