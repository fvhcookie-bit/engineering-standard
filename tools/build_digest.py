#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_digest.py — генерация ИИ-дайджеста ядра (ROADMAP B-9).

Собирает standards/DIGEST.md из standards/ENGINEERING_PRINCIPLES.md: на каждый
принцип — ID, класс, заголовок, дословный абзац «Требование», гейты Q-xx и
вычисленные при генерации диапазоны строк полного текста («EP:101–126»).

Диапазоны верны по построению: они вычисляются из текущего файла, а не пишутся
руками, поэтому правка EP не может протухнуть незаметно — актуальность
проверяется пересборкой (`--check`, шаг CI).

DIGEST.md руками не редактируется: правки только через EP + пересборку.

Языки:
  --lang ru (по умолчанию) — standards/DIGEST.md, дословно из EP;
  --lang en — standards/en/DIGEST.md, официальный перевод: заголовки,
      классы и требования берутся из tools/digest_en.py (канон — русская
      редакция; диапазоны EP:nnn остаются ссылками в русский текст).
      Отсутствующий перевод для ID — ошибка сборки (fail-closed).

Запуск:  python tools/build_digest.py [--lang ru|en]
         python tools/build_digest.py [--lang ru|en] --check  — fail CI
Выход:   0 — ок; 1 — дайджест не соответствует пересборке.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from digest_en import CLASS_EN, DOMAIN_EN, MERGED_EN, MERGED_PREFIX, OUTSIDE, TEXT_EN  # noqa: E402

EP = ROOT / "standards" / "ENGINEERING_PRINCIPLES.md"
DIGEST = ROOT / "standards" / "DIGEST.md"
DIGEST_EN = ROOT / "standards" / "en" / "DIGEST.md"

HEAD = re.compile(r"^## ([A-H]\d)\. \[([^\]]+)\]\s*(.+?)\s*$")
DOMAIN = re.compile(r"^# (Домен [A-H].+?)\s*$")
STOP = re.compile(r"^# Итоговая")
GATE = re.compile(r"\bQ-\d{2}\b")
VERSION = re.compile(r"\*\*Версия:\*\*\s*([\d.]+)")


def _section_end(lines: list[str], start0: int) -> int:
    """1-based последняя содержательная строка раздела (до следующего заголовка)."""
    j = start0 + 1
    while j < len(lines) and not (
        DOMAIN.match(lines[j]) or HEAD.match(lines[j]) or STOP.match(lines[j])
    ):
        j += 1
    end = j
    while end > start0 + 1 and lines[end - 1].strip() in ("", "---"):
        end -= 1
    return end


def _requirement(lines: list[str], start0: int, end1: int) -> str:
    """Дословный абзац «Требование»; для заглушки — её текст-указатель."""
    body = lines[start0 + 1:end1]
    for k, ln in enumerate(body):
        if ln.startswith("**Требование.**"):
            text = ln[len("**Требование.**"):].strip()
            m = k + 1
            while m < len(body) and body[m].strip() and not body[m].startswith("**"):
                text += " " + body[m].strip()
                m += 1
            return text
    para: list[str] = []
    for ln in body:
        s = ln.strip()
        if not s:
            if para:
                break
            continue
        para.append(s)
    return " ".join(para)


def _domain_en(ru_title: str) -> str:
    m = re.match(r"Домен ([A-H])", ru_title)
    if m:
        return DOMAIN_EN[m.group(1)]
    return OUTSIDE


def _class_en(cls: str) -> str:
    if cls.startswith(MERGED_PREFIX):
        return f"{MERGED_EN} {cls[len(MERGED_PREFIX):].strip()}"
    return CLASS_EN.get(cls, cls)


def build(lang: str = "ru") -> str:
    if lang == "en":
        out = _build_en()
    else:
        out = _build_ru()
    return out


def _build_ru() -> str:
    text = EP.read_text(encoding="utf-8")
    lines = text.splitlines()
    vm = VERSION.search(text)
    ep_version = vm.group(1) if vm else "?"

    groups: list[tuple[str, int, list[tuple[int, re.Match[str]]]]] = []
    cur: tuple[str, int, list[tuple[int, re.Match[str]]]] | None = None
    for i, ln in enumerate(lines):
        if STOP.match(ln):
            break
        dm = DOMAIN.match(ln)
        if dm:
            cur = (dm.group(1), i + 1, [])
            groups.append(cur)
            continue
        pm = HEAD.match(ln)
        if pm:
            if cur is None:
                cur = ("(вне доменов)", i + 1, [])
                groups.append(cur)
            cur[2].append((i + 1, pm))

    entries_all: list[tuple[str, str]] = []
    rendered: list[tuple[str, list[str]]] = []
    for title, dline, entries in groups:
        blocks: list[str] = []
        for start1, pm in entries:
            end1 = _section_end(lines, start1 - 1)
            req = _requirement(lines, start1 - 1, end1)
            pid, cls, ttl = pm.group(1), pm.group(2), pm.group(3)
            gates = sorted(set(GATE.findall("\n".join(lines[start1:end1]))))
            entries_all.append((pid, cls))
            blocks += [
                f"### {pid} [{cls}] {ttl} — EP:{start1}–{end1}",
                "",
                req,
                "",
                "Гейты: " + (", ".join(gates) if gates else "—"),
                "",
            ]
        rendered.append((f"## {title} — EP:{dline}", blocks))

    live = [e for e in entries_all if not e[1].startswith("слит")]
    obyaz = [e for e in live if e[1] == "ОБЯЗ"]

    out: list[str] = [
        "<!-- Файл ГЕНЕРИРУЕТСЯ tools/build_digest.py из standards/ENGINEERING_PRINCIPLES.md — не редактировать руками. -->",
        "<!-- Пересборка: python tools/build_digest.py; проверка актуальности: python tools/build_digest.py --check (CI: .github/workflows/consistency.yml). -->",
        "",
        "# DIGEST — компактная сводка стандарта для ИИ-контекста",
        "",
        f"**Версия:** {ep_version} · Источник: `standards/ENGINEERING_PRINCIPLES.md`: "
        f"{len(entries_all)} позиций, {len(live)} живых, {len(obyaz)} [ОБЯЗ].",
        "Формат записи: `ID [класс] Заголовок — EP:строки` + дословный абзац «Требование» "
        "+ гейты. Полный текст принципа читается по указанному диапазону строк.",
        "",
    ]
    for domain_heading, blocks in rendered:
        out.append(domain_heading)
        out.append("")
        out += blocks
    return "\n".join(out).rstrip() + "\n"


def _build_en() -> str:
    """Английский дайджест: перевод из tools/digest_en.py, fail-closed по ID."""
    text = EP.read_text(encoding="utf-8")
    lines = text.splitlines()
    vm = VERSION.search(text)
    ep_version = vm.group(1) if vm else "?"

    groups: list[tuple[str, int, list[tuple[int, re.Match[str]]]]] = []
    cur: tuple[str, int, list[tuple[int, re.Match[str]]]] | None = None
    for i, ln in enumerate(lines):
        if STOP.match(ln):
            break
        dm = DOMAIN.match(ln)
        if dm:
            cur = (dm.group(1), i + 1, [])
            groups.append(cur)
            continue
        pm = HEAD.match(ln)
        if pm:
            if cur is None:
                cur = ("(вне доменов)", i + 1, [])
                groups.append(cur)
            cur[2].append((i + 1, pm))

    entries_all: list[tuple[str, str]] = []
    rendered: list[tuple[str, list[str]]] = []
    for title, dline, entries in groups:
        blocks: list[str] = []
        for start1, pm in entries:
            end1 = _section_end(lines, start1 - 1)
            pid, cls, _ru_ttl = pm.group(1), pm.group(2), pm.group(3)
            if pid not in TEXT_EN:
                raise SystemExit(
                    f"build_digest: для принципа {pid} нет английского перевода "
                    f"в tools/digest_en.py — добавьте его (fail-closed)")
            ttl, req = TEXT_EN[pid]
            gates = sorted(set(GATE.findall("\n".join(lines[start1:end1]))))
            entries_all.append((pid, cls))
            blocks += [
                f"### {pid} [{_class_en(cls)}] {ttl} — EP:{start1}–{end1}",
                "",
                req,
                "",
                "Gates: " + (", ".join(gates) if gates else "—"),
                "",
            ]
        rendered.append((f"## {_domain_en(title)} — EP:{dline}", blocks))

    live = [e for e in entries_all if not e[1].startswith("слит")]
    obyaz = [e for e in live if e[1] == "ОБЯЗ"]

    out: list[str] = [
        "<!-- This file is GENERATED by tools/build_digest.py from standards/ENGINEERING_PRINCIPLES.md - do not edit by hand. -->",
        "<!-- Rebuild: python tools/build_digest.py --lang en; freshness check: python tools/build_digest.py --lang en --check (CI: .github/workflows/consistency.yml). -->",
        "",
        "# DIGEST — compact summary of the standard for AI context",
        "",
        f"**Version:** {ep_version} · **Official translation.** The authoritative text is the "
        f"Russian original (`standards/DIGEST.md`, built from `standards/ENGINEERING_PRINCIPLES.md`): "
        f"{len(entries_all)} positions, {len(live)} live, {len(obyaz)} [MANDATORY].",
        "Classes: [MANDATORY] = [ОБЯЗ], [RECOMMENDED] = [РЕК], [COND] = [УСЛ]. "
        "Entry format: `ID [class] Title — EP:lines` + the \"Requirement\" paragraph (translated) + gates. "
        "The EP line ranges point into the Russian authoritative `ENGINEERING_PRINCIPLES.md` and are "
        "recomputed on every rebuild, so a change to the Russian text makes this digest stale until "
        "regenerated (enforced by the freshness check).",
        "",
    ]
    for domain_heading, blocks in rendered:
        out.append(domain_heading)
        out.append("")
        out += blocks
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Генерация DIGEST.md (ROADMAP B-9)")
    ap.add_argument("--lang", choices=("ru", "en"), default="ru",
                    help="ru — дословный дайджест; en — официальный перевод (digest_en.py)")
    ap.add_argument("--check", action="store_true",
                    help="не перезаписывать; exit 1, если дайджест устарел")
    args = ap.parse_args()

    fresh = build(args.lang)
    target = DIGEST if args.lang == "ru" else DIGEST_EN
    if args.check:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current != fresh:
            print(f"build_digest: {target.relative_to(ROOT)} устарел — "
                  f"пересоберите: python tools/build_digest.py --lang {args.lang}")
            return 1
        print(f"build_digest: {target.relative_to(ROOT)} актуален")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fresh, encoding="utf-8", newline="\n")
    print(f"build_digest: {target.relative_to(ROOT)} пересобран ({len(fresh.splitlines())} строк)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
