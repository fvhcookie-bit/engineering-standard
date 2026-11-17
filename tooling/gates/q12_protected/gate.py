"""Q-12 «Эталоны и правила» (guard-гейт, TASK §3.3).

Защищённые пути (golden/snapshot-эталоны, тесты): метки rule-change /
test-change ставит гейт по дифу; новое эталон-«оракул» в одном PR с изменением
кода — усиленное ревью (агент не назначает собственное поведение оракулом);
файл под несколькими guard-гейтами — обе метки и наивысший подписант (Б-12).
"""

from __future__ import annotations

from typing import Any

from core.files import glob_matches
from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "Q-12"
GATE_VERSION = "1.0.0"


class Q12ProtectedGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        protected: list[dict[str, Any]] = config.get("protected_paths", [])
        code_globs: list[str] = config.get("code_globs", ["src/**"])
        q11_config_globs: list[str] = config.get("q11_config_globs", [])

        # проход 1: трогается ли код в этом PR (нужно для проверки Б-11)
        code_touched = any(
            fd.added and any(glob_matches(fd.path, g) for g in code_globs)
            for fd in inputs.diff
            if not fd.is_binary
        )
        protected_touched = False

        for fd in inputs.diff:
            if fd.is_binary:
                continue
            for entry in protected:
                glob = str(entry.get("glob", ""))
                label = str(entry.get("label", "rule-change"))
                if not glob_matches(fd.path, glob):
                    continue
                protected_touched = True
                result.labels.append(label)
                result.second_reviewer_required = True
                result.findings.append(Finding(
                    code="PROTECTED_PATH_TOUCHED", severity="info",
                    path=fd.path, line=0,
                    message=(f"изменён защищённый путь ({entry.get('category', 'protected')}): "
                             f"метка {label}, ревью владельца + второй проверяющий"),
                ))
                # Б-11: новый оракул в том же PR, где меняется код
                if entry.get("oracle") and fd.is_new and code_touched:
                    result.findings.append(Finding(
                        code="GOLDEN_ORACLE_WITH_CODE", severity="warning",
                        path=fd.path, line=0,
                        message=("новый эталон-оракул добавлен в одном PR с изменением кода — "
                                 "усиленное ревью: агент не назначает собственное поведение оракулом"),
                    ))
                    result.second_reviewer_required = True
                # Б-12: файл под несколькими guard-гейтами (например, ещё и конфиг Q-11)
                if any(glob_matches(fd.path, g) for g in q11_config_globs):
                    result.labels.append("gates-change")
                    result.findings.append(Finding(
                        code="OVERLAP_HIGHEST_SIGNER", severity="info",
                        path=fd.path, line=0,
                        message=("файл под несколькими guard-гейтами: обе метки и подпись "
                                 "наивысшего подписанта (§5 EXCEPTIONS_POLICY)"),
                    ))

        if protected_touched:
            result.labels.append("second-reviewer-required")
        result.stats = {"protected_files": len({
            fd.path for fd in inputs.diff
            if any(glob_matches(fd.path, str(e.get("glob", ""))) for e in protected)
        })}
        return result.finalize()
