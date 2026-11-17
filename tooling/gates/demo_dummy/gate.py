"""Демонстрационный гейт (M1): полный цикл CI→метка→аннотация.

Правило демо: любая ДОБАВЛЕННАЯ строка с маркером FORBIDDEN-DEMO — error
DEMO_FORBIDDEN_MARKER; при наличии находок бот ставит метку demo-label.
Только добавленные строки; удалённые не считаются.
"""

from __future__ import annotations

from typing import Any

from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "DEMO-01"
GATE_VERSION = "1.0.0"
MARKER = "FORBIDDEN-DEMO"
FINDING_MARKER = "DEMO_FORBIDDEN_MARKER"
LABEL = "demo-label"


class DemoGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(
            gate_id=GATE_ID,
            gate_version=GATE_VERSION,
            status=Status.OK,
        )
        added_total = 0
        scanned_files = 0
        for fd in inputs.diff:
            if fd.is_binary:
                continue
            scanned_files += 1
            added_total += len(fd.added)
            for line_no, text in fd.added:
                if MARKER in text:
                    result.findings.append(Finding(
                        code=FINDING_MARKER,
                        severity="error",
                        path=fd.path,
                        line=line_no,
                        message="добавлена строка с запрещённым демо-маркером FORBIDDEN-DEMO",
                        evidence=text.strip()[:120],
                    ))
        result.stats = {"added_lines": added_total, "files_scanned": scanned_files}
        if result.findings:
            result.labels.append(LABEL)
        return result.finalize()
