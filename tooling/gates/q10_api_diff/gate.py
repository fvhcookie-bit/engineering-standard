"""Q-10 «api-diff и совместимость» (обёртка, TASK §3.6).

Запускает внешний инструмент сравнения публичных поверхностей (api-diff) для
каждого затронутого языка; результат инструмента — JSON-список изменений:
[{"path": "...", "symbol": "...", "kind": "api-change" | "breaking"}].

Метки `api-change`/`breaking` ставит гейт по результатам инструмента (не автор).
Для языка без инструмента -> UNAVAILABLE с явной причиной (не молчаливый OK).
Безопасность: команда инструмента — только из конфига (доверенный источник);
содержимое репозитория в shell не передаётся.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

from core.dictionary import language_of
from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "Q-10"
GATE_VERSION = "1.0.0"


class Q10ApiDiffGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        tools: dict[str, list[str]] = {
            t["language"]: t["cmd"] for t in config.get("tools", [])
        }
        ext_map: dict[str, list[str]] = config.get(
            "language_ext", {"python": [".py"]})
        base = str(config.get("base", "main"))
        head = str(config.get("head", "HEAD"))

        touched_languages: set[str] = set()
        for fd in inputs.diff:
            if fd.is_binary or fd.is_deleted:
                continue
            lang = language_of(fd.path, ext_map)
            if lang is not None:
                touched_languages.add(lang)

        if not touched_languages:
            result.stats = {"languages": 0, "tools_run": 0}
            return result.finalize()

        missing = sorted(lang for lang in touched_languages if lang not in tools)
        if missing:
            result.status = Status.UNAVAILABLE
            result.reason = (f"для затронутых языков нет api-diff инструмента: "
                             f"{', '.join(missing)} (не молчаливый OK)")
            return result.finalize()

        breaking = 0
        api_changes = 0
        tools_run = 0
        for lang in sorted(touched_languages):
            cmd = [a.replace("{base}", base).replace("{head}", head)
                   for a in tools[lang]]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            except (OSError, subprocess.TimeoutExpired) as exc:
                # нет бинарника / прав / инструмент завис — не молчаливый OK
                result.status = Status.UNAVAILABLE
                result.reason = (f"api-diff инструмент для {lang} не выполнен "
                                 f"(отсутствует или тайм-аут 600 с): {exc}")
                return result.finalize()
            if proc.returncode != 0:
                result.status = Status.UNAVAILABLE
                result.reason = f"api-diff инструмент для {lang} завершился с ошибкой {proc.returncode}"
                return result.finalize()
            tools_run += 1
            try:
                changes = json.loads(proc.stdout)
            except json.JSONDecodeError:
                result.status = Status.UNAVAILABLE
                result.reason = f"api-diff инструмент для {lang} вернул не-JSON вывод"
                return result.finalize()
            for change in changes:
                kind = str(change.get("kind", "api-change"))
                if kind == "breaking":
                    breaking += 1
                    result.findings.append(Finding(
                        code="API_BREAKING", severity="error",
                        path=str(change.get("path", "")), line=0,
                        message=(f"breaking-изменение публичной поверхности "
                                 f"({change.get('symbol', '')}) — метка breaking"),
                    ))
                else:
                    api_changes += 1
                    result.findings.append(Finding(
                        code="API_CHANGE", severity="warning",
                        path=str(change.get("path", "")), line=0,
                        message=f"изменение публичной поверхности ({change.get('symbol', '')})",
                    ))

        if breaking:
            result.labels.append("breaking")
            result.second_reviewer_required = True
        if breaking or api_changes:
            result.labels.append("api-change")

        result.stats = {"languages": len(touched_languages),
                        "tools_run": tools_run,
                        "breaking": breaking,
                        "api_changes": api_changes}
        return result.finalize()
