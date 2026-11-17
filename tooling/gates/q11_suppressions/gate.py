"""Q-11 «Подавления и конфигурации гейтов» (guard-гейт, TASK_guard-gates §3.1).

Семантика (критично для понимания):
- подавление БЕЗ валидного EX-ID (E-A) учитывается в храповике baseline: рост любого
  счётчика по (вид, glob) — FAIL, компенсации запрещены (Б-8);
- подавление С валидным EX-ID (E-C) из реестра — легитимно в этом PR, из
  baseline-подсчёта исключается и остаётся под наблюдением Q-19;
- декларации автора PR в гейт не поступают (независимые источники, Б-1);
- метки gates-change ставит runner по результатам прогона (новый/изменённый
  конфиг-файл, изменение fingerprint).
"""

from __future__ import annotations

import re
from typing import Any

from core.config_fingerprint import detect_tool, fingerprint
from core.dictionary import language_of
from core.files import glob_matches
from core.gate_api import Finding, GateInputs, GateResult, Status

GATE_ID = "Q-11"
GATE_VERSION = "1.0.0"

EX_ANCHOR = re.compile(r"EX-\d{4}-\d{3}")


class Q11SuppressionsGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        patterns = config["patterns"]
        ext_map = config.get("language_ext", {"python": [".py"]})
        config_globs: list[str] = config.get("config_files", [])
        baseline_globs: list[str] = config.get("baseline_paths", ["baseline/**", "dictionaries/**"])
        heavy_threshold = int(config.get("second_reviewer_threshold", 3))

        exceptions = {e.id: e for e in inputs.registries.exceptions}
        baseline = inputs.registries.baseline
        counts_by_kind = baseline.get("counts", {})

        total_suppressions = 0
        baseline_relevant: dict[str, list[str]] = {}  # kind -> пути подавлений без EX
        saw_baseline_path = False
        saw_code_path = False

        for fd in inputs.diff:
            if fd.is_binary:
                continue
            is_baseline = any(glob_matches(fd.path, g) for g in baseline_globs)
            has_content = bool(fd.added) or fd.removed_count > 0
            if is_baseline and has_content:
                saw_baseline_path = True
            if (not is_baseline) and has_content:
                saw_code_path = True

            # (5) появление конфиг-файла инструмента -> gates-change
            if any(glob_matches(fd.path, g) for g in config_globs):
                result.labels.append("gates-change")
                result.findings.append(Finding(
                    code="CONFIG_FILE_TOUCHED", severity="info", path=fd.path, line=1,
                    message="изменён конфиг-файл инструмента — метка gates-change обязательна",
                ))

            lang = language_of(fd.path, ext_map)
            if lang is None:
                continue
            for line_no, text in fd.added:
                for pat in patterns:
                    if lang not in pat.languages:
                        continue
                    if not pat.regex.search(text):
                        continue
                    total_suppressions += 1
                    anchor = EX_ANCHOR.search(text)
                    kind_for_baseline = pat.id
                    if anchor is None:
                        result.findings.append(Finding(
                            code="SUPPRESS_NO_EXID", severity="error",
                            path=fd.path, line=line_no,
                            message="новое подавление без причины и EX-ID из реестра",
                            evidence=text.strip()[:120],
                        ))
                    else:
                        ex_id = anchor.group(0)
                        entry = exceptions.get(ex_id)
                        if entry is None:
                            result.findings.append(Finding(
                                code="SUPPRESS_UNKNOWN_EXID", severity="error",
                                path=fd.path, line=line_no,
                                message=f"EX-ID {ex_id} отсутствует в EXCEPTIONS.md",
                                evidence=text.strip()[:120],
                            ))
                        elif entry.is_expired():
                            result.findings.append(Finding(
                                code="SUPPRESS_EXID_EXPIRED", severity="error",
                                path=fd.path, line=line_no,
                                message=f"срок пересмотра {ex_id} истёк",
                                evidence=str(entry.review_due),
                            ))
                        else:
                            # легитимное E-C: из baseline-подсчёта исключается
                            kind_for_baseline = ""
                            result.stats["ec_suppressions"] = result.stats.get("ec_suppressions", 0) + 1
                    if kind_for_baseline:
                        baseline_relevant.setdefault(kind_for_baseline, []).append(fd.path)

        # (3) храповик: рост любого счётчика, без взаимных компенсаций
        for kind, paths in sorted(baseline_relevant.items()):
            globs: dict[str, int] = counts_by_kind.get(kind, {})
            allowed = sum(
                maxv for glob, maxv in globs.items()
                if any(glob_matches(p, glob) for p in paths)
            )
            if len(paths) > allowed:
                result.findings.append(Finding(
                    code="BASELINE_GROWTH", severity="error",
                    path=paths[0], line=0,
                    message=(f"вид {kind}: добавлено {len(paths)}, разрешено baseline {allowed}; "
                             "компенсации запрещены"),
                ))

        # (4) более 3 подавлений на PR — второй ревьюер
        if total_suppressions > heavy_threshold:
            result.second_reviewer_required = True
            result.labels.append("second-reviewer-required")

        # (5б) fingerprint: изменение эффективной конфигурации
        fingerprint_section = baseline.get("fingerprint", {})
        for fd in inputs.diff:
            tool = detect_tool(fd.path)
            if tool is None or not fd.added and fd.removed_count == 0:
                continue
            head_text = inputs.files.read(fd.path)
            if head_text is None:
                continue
            fp = fingerprint(head_text, tool)
            known = fingerprint_section.get(tool, {}).get(fd.path)
            if fp is not None and known is not None and fp != known:
                result.labels.append("gates-change")
                result.findings.append(Finding(
                    code="CONFIG_FINGERPRINT_CHANGED", severity="warning",
                    path=fd.path, line=1,
                    message="эффективная конфигурация инструмента изменилась (fingerprint)",
                ))

        # (6) baseline и код в одном PR — запрещено
        if saw_baseline_path and saw_code_path:
            result.findings.append(Finding(
                code="BASELINE_WITH_CODE", severity="error",
                path="baseline", line=0,
                message="изменение baseline и кода в одном PR (baseline-reset — отдельный PR)",
            ))

        result.stats.update({
            "suppressions_new": total_suppressions,
            "second_reviewer_threshold": heavy_threshold,
        })
        return result.finalize()
