#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doc_consistency.py — механизм консистентности собственных документов (ROADMAP A-3).

Находки-источники: GE-9, OP-22 (см. standards/review/REVIEWS_STATUS.md); урок «G3 vs G-08».

Проверки (ошибка = fail CI):
  LINKS       markdown-ссылки [..](..) ведут на существующие файлы
  FILES       упоминания путей этого репозитория в `code-spans` существуют
              (user/… — локальный архив владельца, вне репозитория, пропускается)
  SECTIONS    §N[.M] (в т.ч. диапазоны §N–M) — заголовок существует хотя бы в одном
              документе-кандидате (текущий + поименованные в той же строке);
              для README/ROADMAP/REVIEWS_STATUS ссылка без имени документа в строке
              пропускается (там кросс-ссылки доминируют над ссылками «на себя»);
              «см. N» / «раздел N» — в текущем документе (ядро и guidelines)
  GATES       Q-xx существует в каталоге QUALITY_GATES; каталог непрерывен от Q-01;
              устаревшие G-xx (идентификаторы до v1.1) — ошибка
  PRINCIPLES  A1…H9 существуют в ENGINEERING_PRINCIPLES
  SCENARIOS   Б-xx существует в матрице TASK_guard-gates
  TASKS       ID задач [A-D]-N существуют в таблице ROADMAP
  STAGES      M-N существует в этапах TASK_guard-gates
  VERSIONS    у каждого документа ядра есть ровно одна **Версия:**; все равны последней
              записи changelog TRACEABILITY; README упоминает v<эта версия>
  TERMS       несущие термины §0.7 EP не переопределяются в других документах
              (единый источник — требование самого §0.7)
  CLAIMS      заявленные количества («N принцип(а/ов)», диапазон «Q-01…Q-19»)
              совпадают с фактическими
  SEQ         нумерованные разделы каждого документа идут строго по возрастанию

Границы:
  - архив ревью (standards/review/review_*.md) проверяется только на LINKS —
    исторические идентификаторы (G-xx, счётчики v1.0) и цитаты там легитимны;
  - REVIEWS_STATUS.md исключён из GATES/CLAIMS (цитирует находки до v1.1);
  - якорные ссылки (#…) и внешние URL не проверяются.

Запуск:  python tools/doc_consistency.py [--json]
Выход:   0 — ошибок нет; 1 — есть ошибки.
Детерминизм: одинаковые документы дают одинаковый отчёт (стабильная сортировка,
меток времени нет — см. QUALITY_GATES §4, требование к отчётам гейтов).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def md_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def rparts(p: Path) -> tuple[str, ...]:
    """Части пути относительно корня репозитория (p.parts на Windows начинаются с диска)."""
    return p.relative_to(ROOT).parts


CORE = [p for p in md_files() if rparts(p)[0] == "standards" and "review" not in rparts(p)]
GUIDELINES = [p for p in md_files() if rparts(p)[0] == "guidelines"]
ROOT_DOCS = [ROOT / "README.md", ROOT / "ROADMAP.md"]
STATUS = ROOT / "standards" / "review" / "REVIEWS_STATUS.md"
ARCHIVE = [p for p in md_files()
           if rparts(p)[:2] == ("standards", "review") and p.name.startswith("review_")]

CHECKED = CORE + GUIDELINES + ROOT_DOCS + [STATUS]

EP = ROOT / "standards" / "ENGINEERING_PRINCIPLES.md"
QG = ROOT / "standards" / "QUALITY_GATES.md"
TRACE = ROOT / "standards" / "TRACEABILITY.md"
TASK = ROOT / "guidelines" / "TASK_guard-gates.md"
README = ROOT / "README.md"

TEXTS: dict[str, str] = {rel(p): p.read_text(encoding="utf-8") for p in md_files()}

NAME2PATH: dict[str, Path] = {}
for _p in md_files():
    NAME2PATH.setdefault(_p.name, _p)

ABBREVIATIONS = {
    "ENGINEERING_PRINCIPLES": "ENGINEERING_PRINCIPLES.md",
    "QUALITY_GATES": "QUALITY_GATES.md",
    "AI_AGENT_RULES": "AI_AGENT_RULES.md",
    "EXCEPTIONS_POLICY": "EXCEPTIONS_POLICY.md",
    "IMPLEMENTATION_GUIDE": "IMPLEMENTATION_GUIDE.md",
    "TRACEABILITY": "TRACEABILITY.md",
    "GUIDELINE_development": "GUIDELINE_development.md",
    "GUIDELINE_profiles_and_dictionaries": "GUIDELINE_profiles_and_dictionaries.md",
    "TASK_guard-gates": "TASK_guard-gates.md",
    "REVIEWS_STATUS": "REVIEWS_STATUS.md",
    "ROADMAP": "ROADMAP.md",
    "EP": "ENGINEERING_PRINCIPLES.md",
    "QG": "QUALITY_GATES.md",
    "ИГ": "IMPLEMENTATION_GUIDE.md",
    "AAR": "AI_AGENT_RULES.md",
    "EXCEPTIONS": "EXCEPTIONS_POLICY.md",
    "TASK": "TASK_guard-gates.md",
}
ABBR_RE = re.compile(
    r"\b(" + "|".join(sorted(ABBREVIATIONS, key=len, reverse=True)) + r")\b")

FINDINGS: list[dict] = []


def err(code: str, path: Path, line: int, message: str) -> None:
    FINDINGS.append({"code": code, "file": rel(path), "line": line, "message": message})


def lines_of(p: Path) -> list[str]:
    return TEXTS[rel(p)].splitlines()


# --- эталонные множества (парсинг «источников истины») -----------------------

NUM_HEADING = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)\.?(?:\s|$)")

_sections_cache: dict[str, set[str]] = {}


def sections_of(p: Path) -> set[str]:
    key = rel(p)
    if key not in _sections_cache:
        out: set[str] = set()
        for ln in lines_of(p):
            m = NUM_HEADING.match(ln)
            if m:
                out.add(m.group(1))
        _sections_cache[key] = out
    return _sections_cache[key]


def principle_ids() -> set[str]:
    out = set()
    for ln in lines_of(EP):
        m = re.match(r"^## ([A-H]\d)\.", ln)
        if m:
            out.add(m.group(1))
    return out


def gate_ids() -> set[str]:
    out = set()
    for ln in lines_of(QG):
        m = re.match(r"^### (Q-\d{2})\b", ln)
        if m:
            out.add(m.group(1))
    return out


def scenario_ids() -> set[int]:
    out = set()
    for ln in lines_of(TASK):
        m = re.match(r"^\|\s*Б-(\d{1,2})\s*\|", ln)
        if m:
            out.add(int(m.group(1)))
    return out


def stage_ids() -> set[str]:
    out = set()
    for ln in lines_of(TASK):
        m = re.match(r"^\|\s*(M\d)\s*\|", ln)
        if m:
            out.add(m.group(1))
    return out


def roadmap_task_ids() -> set[str]:
    out = set()
    for ln in lines_of(ROOT / "ROADMAP.md"):
        m = re.match(r"^\|\s*([A-D])-(\d+)\s*\|", ln)
        if m:
            out.add(f"{m.group(1)}-{m.group(2)}")
    return out


def changelog_latest() -> tuple[int, ...]:
    """Последняя версия из таблицы §5 TRACEABILITY (не из других таблиц документа)."""
    vals: list[tuple[int, ...]] = []
    in_changelog = False
    for ln in lines_of(TRACE):
        if re.match(r"^#{1,6}\s+5\.", ln):
            in_changelog = True
            continue
        if in_changelog and re.match(r"^#{1,6}\s", ln):
            break
        if in_changelog:
            m = re.match(r"^\|\s*([\d.]+)\s*\|", ln)
            if m:
                vals.append(tuple(int(x) for x in m.group(1).split(".")))
    return max(vals) if vals else ()


# --- проверяемые паттерны ----------------------------------------------------

MDLINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MENTION = re.compile(r"`((?:\.\./|\./)?(?:standards|guidelines|tools|user)/[^`\s]+)`")
SEC = re.compile(r"§\s*(\d+(?:\.\d+)*)(?:\s*[–—-]\s*(\d+(?:\.\d+)*))?")
FREF = re.compile(r"([\w.\-]+\.md)")
SEE_NUM = re.compile(r"(?:[Сс]м\.|[Рр]аздел\w*)\s+(\d+(?:\.\d+)*)")
GATE_REF = re.compile(r"\bQ-(\d{2})\b")
GATE_RANGE = re.compile(r"\bQ-(\d{2})\s*…\s*Q-(\d{2})")
OLD_GATE = re.compile(r"\bG-(\d{2})\b")
PRIN_REF = re.compile(r"\b([A-H])([1-9])\b")
SCEN_REF = re.compile(r"\bБ-(\d{1,2})\b")
TASK_REF = re.compile(r"\b([A-D])-\d+\b")
STAGE_REF = re.compile(r"\bM([1-9])\b")
VERSION = re.compile(r"\*\*Версия:\*\*\s*([\d.]+)")
CLAIM_PRINCIPLES = re.compile(r"\b(\d+)\s+принцип\w*")

# Легитимные исключения (заполняется только с обоснованием в tools/README.md).
PERMIT: dict[tuple[str, str], str] = {
    # ROADMAP, задача A-3: «уроки G3 vs G-08» — историческое упоминание дефекта
    # ссылок v1.0, а не ссылка на гейт (гейты с v1.1 переименованы в Q-xx).
    ("ROADMAP.md", "G-08"): "историческое упоминание дефекта v1.0 (урок для A-3)",
}


def _num_or_parent(x: str, nums: set[str]) -> bool:
    """Точный раздел или ближайший родитель («1.5.2» → «1.5» → «1»).

    Ссылки на подпункты нумерованных списков внутри раздела (например,
    «§1.5.2–3» — пункты 2–3 списка §1.5 QUALITY_GATES) легитимны: заголовком
    является только родительский раздел.
    """
    parts = x.split(".")
    while parts:
        if ".".join(parts) in nums:
            return True
        parts.pop()
    return False


def candidate_docs(f: Path, line: str) -> set[Path]:
    """Документы-кандидаты для §-ссылки: текущий + поименованные в строке."""
    docs = {f}
    for m in FREF.finditer(line):
        p = NAME2PATH.get(m.group(1).split("/")[-1])
        if p is not None:
            docs.add(p)
    for m in ABBR_RE.finditer(line):
        p = NAME2PATH.get(ABBREVIATIONS[m.group(1)])
        if p is not None:
            docs.add(p)
    return docs


def run_checks() -> None:
    gates = gate_ids()
    princ = principle_ids()
    scen = scenario_ids()
    tasks = roadmap_task_ids()
    stages = stage_ids()
    latest = changelog_latest()
    latest_str = ".".join(str(x) for x in latest)

    for f in CHECKED:
        is_core = f in CORE
        is_aggregator = f in ROOT_DOCS or f == STATUS
        for i, ln in enumerate(lines_of(f), 1):
            permit_key = (rel(f), ln.strip())

            # LINKS + FILES (FILES — только для проверяемого набора)
            for m in MDLINK.finditer(ln):
                href = m.group(1)
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if not (f.parent / href.split("#")[0]).resolve().exists():
                    err("LINKS", f, i, f"битая ссылка: {href}")
            if f in CHECKED:
                for m in MENTION.finditer(ln):
                    p = m.group(1)
                    if p.startswith("user/"):
                        continue  # локальный архив владельца, вне репозитория
                    base = f.parent if p.startswith("..") else ROOT
                    if not (base / p).resolve().exists():
                        err("FILES", f, i, f"упомянутый файл отсутствует: {p}")

            # SECTIONS
            for m in SEC.finditer(ln):
                docs = candidate_docs(f, ln)
                if f == STATUS:
                    docs |= set(ARCHIVE)  # находки REVIEWS_STATUS ссылаются на разделы самих ревью
                if is_aggregator and docs == {f}:
                    continue  # кросс-ссылка без имени документа — неоднозначно
                for x in filter(None, (m.group(1), m.group(2))):
                    if not any(_num_or_parent(x, sections_of(d)) for d in docs):
                        names = ", ".join(sorted(rel(d) for d in docs))
                        err("SECTIONS", f, i,
                            f"нет заголовка §{x} ни в одном из: {names} (ссылка «{m.group(0).strip()}»)")
            if is_core or f in GUIDELINES:
                for m in SEE_NUM.finditer(ln):
                    if m.group(1) not in sections_of(f):
                        err("SECTIONS", f, i,
                            f"«{m.group(0).strip()}»: в {rel(f)} нет раздела {m.group(1)}")

            # GATES (архив ревью и REVIEWS_STATUS исключены: исторические ID легитимны)
            if f in CORE + GUIDELINES + ROOT_DOCS:
                for m in GATE_REF.finditer(ln):
                    tok = f"Q-{m.group(1)}"
                    if tok not in gates and (rel(f), tok) not in PERMIT:
                        err("GATES", f, i, f"неизвестный гейт {tok} (нет в каталоге QUALITY_GATES)")
                for m in GATE_RANGE.finditer(ln):
                    for x in (m.group(1), m.group(2)):
                        if f"Q-{x}" not in gates:
                            err("GATES", f, i, f"диапазон ссылается на несуществующий гейт Q-{x}")
                for m in OLD_GATE.finditer(ln):
                    if (rel(f), m.group(0)) in PERMIT:
                        continue
                    err("GATES", f, i,
                        f"устаревший ID гейта {m.group(0)} — с v1.1 гейты Q-xx (TRACEABILITY §5)")

            # PRINCIPLES
            for m in PRIN_REF.finditer(ln):
                tok = m.group(0)
                if tok not in princ and (rel(f), tok) not in PERMIT:
                    err("PRINCIPLES", f, i,
                        f"неизвестный принцип {tok} (нет в ENGINEERING_PRINCIPLES)")

            # SCENARIOS / STAGES
            if f in GUIDELINES + ROOT_DOCS + [STATUS]:
                for m in SCEN_REF.finditer(ln):
                    if int(m.group(1)) not in scen:
                        err("SCENARIOS", f, i,
                            f"сценарий {m.group(0)} отсутствует в матрице TASK_guard-gates")
                for m in STAGE_REF.finditer(ln):
                    if f"M{m.group(1)}" not in stages:
                        err("STAGES", f, i,
                            f"этап {m.group(0)} отсутствует в TASK_guard-gates §6")

            # TASKS
            for m in TASK_REF.finditer(ln):
                if m.group(0) not in tasks:
                    err("TASKS", f, i, f"задача {m.group(0)} отсутствует в таблице ROADMAP")

    # SEQ: нумерация разделов строго по возрастанию
    for f in CHECKED:
        prev: tuple[int, ...] | None = None
        for i, ln in enumerate(lines_of(f), 1):
            m = NUM_HEADING.match(ln)
            if m:
                t = tuple(int(x) for x in m.group(1).split("."))
                if prev is not None and t <= prev:
                    err("SEQ", f, i,
                        f"нумерация разделов не возрастает: {m.group(1)} после "
                        f"{'.'.join(str(x) for x in prev)}")
                prev = t

    # VERSIONS
    for f in CORE:
        found = VERSION.findall(TEXTS[rel(f)])
        if not found:
            err("VERSIONS", f, 1, "нет пометки **Версия:**")
        elif len(found) > 1:
            err("VERSIONS", f, 1, f"несколько пометок версии: {found}")
        elif tuple(int(x) for x in found[0].split(".")) != latest:
            err("VERSIONS", f, 1,
                f"версия {found[0]} не равна последней записи changelog TRACEABILITY ({latest_str})")
    if latest and f"v{latest_str}" not in TEXTS[rel(README)]:
        err("VERSIONS", README, 1, f"README не упоминает актуальную версию v{latest_str}")

    # TERMS: несущие термины §0.7 определяются только в EP
    terms: list[str] = []
    in_07 = False
    for ln in lines_of(EP):
        if ln.startswith("### 0.7"):
            in_07 = True
            continue
        if in_07 and re.match(r"^#{1,6}\s", ln):
            break
        if in_07:
            m = re.match(r"^- \*\*(.+?)\*\*", ln)
            if m:
                terms.append(m.group(1))
    for f in CORE:
        if f == EP:
            continue
        for i, ln in enumerate(lines_of(f), 1):
            for term in terms:
                if re.match(rf"^\s*(?:[-*]\s+)?\*\*{re.escape(term)}\*\*\s*—", ln):
                    err("TERMS", f, i,
                        f"термин «{term}» переопределён вне §0.7 ENGINEERING_PRINCIPLES "
                        f"(нарушение единого источника)")

    # CLAIMS: заявленные количества = фактические
    princ_n = len(princ)
    for f in (README, EP):
        for i, ln in enumerate(lines_of(f), 1):
            if ln.lstrip().startswith("|"):
                continue  # таблицы (в т.ч. исторический changelog) не заявляют текущее
            for m in CLAIM_PRINCIPLES.finditer(ln):
                if int(m.group(1)) != princ_n:
                    err("CLAIMS", f, i,
                        f"заявлено {m.group(1)} принципов, фактически в EP — {princ_n}")
            for m in GATE_RANGE.finditer(ln):
                lo, hi = int(m.group(1)), int(m.group(2))
                actual_hi = max(int(g[2:]) for g in gates)
                if lo != 1 or hi != actual_hi:
                    err("CLAIMS", f, i,
                        f"диапазон гейтов Q-{m.group(1)}…Q-{m.group(2)} не совпадает "
                        f"с каталогом (Q-01…Q-{actual_hi:02d})")

    # Целостность каталога гейтов
    expected = [f"Q-{i:02d}" for i in range(1, len(gates) + 1)]
    if sorted(gates) != expected:
        missing = sorted(set(expected) - set(gates))
        err("GATES", QG, 1, f"каталог гейтов непрерывен от Q-01; отсутствуют: {missing}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Консистентность документов (ROADMAP A-3)")
    ap.add_argument("--json", action="store_true", help="отчёт в JSON")
    args = ap.parse_args()

    run_checks()
    FINDINGS.sort(key=lambda x: (x["file"], x["line"], x["code"]))

    if args.json:
        print(json.dumps({"errors": len(FINDINGS), "findings": FINDINGS},
                         ensure_ascii=False, indent=2))
    else:
        n = len(CHECKED) + len(ARCHIVE)
        print(f"doc_consistency: проверено файлов: {n}; ошибок: {len(FINDINGS)}")
        for x in FINDINGS:
            print(f"[{x['code']}] {x['file']}:{x['line']} — {x['message']}")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
