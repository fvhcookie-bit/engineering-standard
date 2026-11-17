"""D-1/D-2: агрегация метрик эксплуатации и дашборд (EXCEPTIONS_POLICY §7).

Только агрегаты: содержимое проверяемых файлов нигде не сохраняется
(GUIDELINE_development §9.3). Источники:
- артефакты отчётов `*.report.json` + карточка `*.meta.json`
  ({"author": "...", "pr": 7}) — субъекты: автор/агент;
- `EXCEPTIONS.md` — активные/просроченные исключения по принципам;
- baseline (`suppressions.yaml`) — алерт о застое по `generated_at`.

Детерминизм: дата подаётся параметром (`today`), не берётся из системы.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from core.registries import parse_exceptions_md


@dataclass
class SubjectStats:
    author: str
    reports: int = 0
    prs: set[int] = field(default_factory=set)
    findings_error: int = 0
    findings_warning: int = 0
    labels: dict[str, int] = field(default_factory=dict)
    gates: dict[str, int] = field(default_factory=dict)
    suppressions_new: int = 0
    ec_suppressions: int = 0


def collect_reports(reports_dir: Path) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Пары (отчёт, мета) из *.report.json + *.meta.json."""
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for path in sorted(reports_dir.glob("*.report.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        meta_path = path.with_name(path.name.replace(".report.json", ".meta.json"))
        meta: dict[str, Any] = {}
        if meta_path.is_file():
            loaded = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                meta = loaded
        pairs.append((report, meta))
    return pairs


def collect_dashboard(
    reports_dir: Path,
    exceptions_text: str | None = None,
    baseline_text: str | None = None,
    today: date | None = None,
    stale_days: int = 90,
) -> dict[str, Any]:
    today = today or date.today()
    subjects: dict[str, SubjectStats] = {}

    for report, meta in collect_reports(reports_dir):
        author = str(meta.get("author", "unknown"))
        st = subjects.setdefault(author, SubjectStats(author=author))
        st.reports += 1
        pr = meta.get("pr")
        if isinstance(pr, int):
            st.prs.add(pr)
        for f in report.get("findings", []):
            if f.get("severity") == "error":
                st.findings_error += 1
            elif f.get("severity") == "warning":
                st.findings_warning += 1
        for label in report.get("labels", []):
            st.labels[label] = st.labels.get(label, 0) + 1
        gate = str(report.get("gate", "?"))
        st.gates[gate] = st.gates.get(gate, 0) + 1
        stats = report.get("stats", {}) or {}
        st.suppressions_new += int(stats.get("suppressions_new", 0))
        st.ec_suppressions += int(stats.get("ec_suppressions", 0))

    dash: dict[str, Any] = {"schema": 1, "stale_days": stale_days}

    dash["subjects"] = [
        {
            "author": s.author,
            "reports": s.reports,
            "prs": len(s.prs),
            "findings_error": s.findings_error,
            "findings_warning": s.findings_warning,
            "labels": dict(sorted(s.labels.items())),
            "gates": dict(sorted(s.gates.items())),
            "suppressions_new": s.suppressions_new,
            "ec_suppressions": s.ec_suppressions,
        }
        for s in sorted(subjects.values(), key=lambda x: x.author)
    ]

    # D-2: исключения (из EXCEPTIONS.md через парсер реестра)
    if exceptions_text is not None:
        entries = parse_exceptions_md(exceptions_text)
        # нормализация: «активное», «Активное», «активное (продлено)» — активные
        active = [e for e in entries
                  if e.status.strip().lower().startswith("активн")]
        expired = [e for e in active if e.is_expired(today)]
        by_principle: dict[str, int] = {}
        for e in active:
            key = e.principle or "(не указан)"
            by_principle[key] = by_principle.get(key, 0) + 1
        dash["exceptions"] = {
            "total": len(entries),
            "active": len(active),
            "expired": len(expired),
            "by_principle": dict(sorted(by_principle.items())),
            "expired_ids": sorted(e.id for e in expired),
        }

    # D-2: застой baseline по generated_at
    if baseline_text is not None:
        import yaml

        data = yaml.safe_load(baseline_text) or {}
        generated_at = str(data.get("generated_at", "")).strip()
        entry: dict[str, Any] = {"stale_days_limit": stale_days}
        if generated_at:
            parts = generated_at[:10].split("-")
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                generated = date(int(parts[0]), int(parts[1]), int(parts[2]))
                age = (today - generated).days
                entry.update({"generated_at": generated_at, "age_days": age,
                              "stale_alert": age > stale_days})
            else:
                entry.update({"stale_alert": True, "reason": "generated_at неразбираем"})
        else:
            entry.update({"stale_alert": True,
                          "reason": "generated_at отсутствует — дата пересчёта неизвестна"})
        dash["baseline"] = entry

    return dash


def render_markdown(dash: dict[str, Any]) -> str:
    out: list[str] = ["# Дашборд эксплуатации (агрегаты)", ""]
    out += ["## Субъекты", "",
            "| Автор | Отчёты | PR | Ошибки | Предупреждения | Замазки (нов.) | E-C |",
            "|---|---|---|---|---|---|---|"]
    for s in dash.get("subjects", []):
        out.append(f"| {s['author']} | {s['reports']} | {s['prs']} | "
                   f"{s['findings_error']} | {s['findings_warning']} | "
                   f"{s['suppressions_new']} | {s['ec_suppressions']} |")
    exc = dash.get("exceptions")
    if exc is not None:
        out += ["", "## Исключения", "",
                f"Активных: {exc['active']}; просроченных: {exc['expired']}.",
                ""]
        for principle, n in exc.get("by_principle", {}).items():
            out.append(f"- {principle}: {n}")
    bl = dash.get("baseline")
    if bl is not None:
        out += ["", "## Baseline", ""]
        if bl.get("stale_alert"):
            reason = bl.get("reason") or (
                f"не пересчитывался дольше {bl['stale_days_limit']} дней "
                f"(возраст {bl.get('age_days', 0)} д.)")
            out.append(f"⚠️ ЗАСТОЙ: {reason}")
        else:
            out.append(f"Ок: возраст {bl.get('age_days')} д. ≤ лимита "
                       f"{bl['stale_days_limit']} д.")
    return "\n".join(out).rstrip() + "\n"


def collect_and_write(reports_dir: Path, out_dir: Path, **kwargs: Any) -> Path:
    dash = collect_dashboard(reports_dir, **kwargs)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dashboard.json").write_text(
        json.dumps(dash, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    (out_dir / "dashboard.md").write_text(render_markdown(dash),
                                          encoding="utf-8", newline="\n")
    return out_dir / "dashboard.json"
