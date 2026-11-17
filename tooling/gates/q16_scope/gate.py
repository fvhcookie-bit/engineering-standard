"""Q-16 «Границы задачи» (TASK §3.5, диф-гигиена).

Список нужных файлов — из трекера по ID задачи (не из описания PR).
- файл вне списка задачи -> FAIL (Б-14);
- списка нет в задаче -> SKIP с явной причиной, не молчаливый OK (Б-13);
- диф > 600 добавленных строк вне механических изменений -> предупреждение;
- трекер недоступен -> UNAVAILABLE (fail-closed).
"""

from __future__ import annotations

from typing import Any

from adapters.base import AdapterUnavailable
from core.files import glob_matches
from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "Q-16"
GATE_VERSION = "1.0.0"


class Q16ScopeGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        task_id = str(config.get("task_id", ""))
        mechanical_globs: list[str] = config.get("mechanical_globs", [])
        line_limit = int(config.get("line_limit", 600))

        if not task_id:
            result.status = Status.SKIP
            result.reason = "в ветке/конфиге нет ID задачи — граница задачи не определена"
            return result.finalize()

        try:
            task_files = inputs.api.get_task_files(task_id)
        except AdapterUnavailable as exc:
            result.status = Status.UNAVAILABLE
            result.reason = f"трекер недоступен: {exc}"
            return result.finalize()

        if task_files is None:
            result.status = Status.SKIP
            result.reason = f"в задаче {task_id} нет списка файлов — гейт не применяется (заявлено прямо)"
            return result.finalize()

        added_lines = 0
        outside: list[str] = []
        for fd in inputs.diff:
            if fd.is_binary:
                continue
            mechanical = any(glob_matches(fd.path, g) for g in mechanical_globs)
            if not mechanical:
                added_lines += len(fd.added)
            if not any(fnmatch_exact(fd.path, allowed) for allowed in task_files):
                outside.append(fd.path)

        for path in sorted(set(outside)):
            result.findings.append(Finding(
                code="SCOPE_OUTSIDE_TASK", severity="error",
                path=path, line=0,
                message=f"файл вне списка задачи {task_id}",
            ))

        if added_lines > line_limit:
            result.findings.append(Finding(
                code="LARGE_DIFF", severity="warning",
                path="PR", line=0,
                message=(f"диф {added_lines} добавленных строк вне механических изменений "
                         f"(> {line_limit}) — предложить декомпозицию"),
            ))

        result.stats = {"files_touched": len({fd.path for fd in inputs.diff}),
                        "files_outside_task": len(set(outside)),
                        "added_lines": added_lines}
        return result.finalize()


def fnmatch_exact(path: str, allowed: str) -> bool:
    """Точное совпадение или явный glob в списке задачи."""
    import fnmatch

    return path == allowed or fnmatch.fnmatch(path, allowed)
