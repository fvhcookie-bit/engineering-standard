"""D-3: метрика зрелости — доля [ОБЯЗ]-правил, исполняемых механикой.

Формула: из итоговой таблицы ENGINEERING_PRINCIPLES считаются правила класса
[ОБЯЗ]; правила с пометкой «процессное» в колонке гейта исполняются
ревью/артефактами процесса, остальные — механикой (гейты/CI).
Публикуется рядом со стандартом (standards/MATURITY.md) с историей по датам
(MATURITY_HISTORY.md) — тренд виден между релизами.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "standards" / "ENGINEERING_PRINCIPLES.md"
OUT = ROOT / "standards" / "MATURITY.md"
HISTORY = ROOT / "standards" / "MATURITY_HISTORY.md"

ROW = re.compile(r"^\| ([A-H]\d) \| (.+?) \| ([А-ЯЁ]{4}(?:\s*\(.+?\))?) \| (.+?) \|$")


def compute(ep_text: str | None = None) -> dict[str, object]:
    text = ep_text if ep_text is not None else (ROOT / "standards" / "ENGINEERING_PRINCIPLES.md").read_text(encoding="utf-8")
    obyaz_total = 0
    obyaz_mechanical = 0
    process_rules: list[str] = []
    for raw in text.splitlines():
        m = ROW.match(raw.strip())
        if not m:
            continue
        rule_id, _name, klass, gate = m.groups()
        if "ОБЯЗ" not in klass:
            continue
        obyaz_total += 1
        if "процессное" in gate:
            process_rules.append(rule_id)
        else:
            obyaz_mechanical += 1
    share = round(100 * obyaz_mechanical / obyaz_total) if obyaz_total else 0
    return {
        "obyaz_total": obyaz_total,
        "obyaz_mechanical": obyaz_mechanical,
        "obyaz_process": len(process_rules),
        "process_rules": process_rules,
        "share_percent": share,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:]
    today = date.fromisoformat(args[0]) if args else date.today()
    data = compute()
    total = data["obyaz_total"]
    mech = data["obyaz_mechanical"]
    share = data["share_percent"]

    OUT.write_text(
        "# Метрика зрелости стандарта (D-3)\n\n"
        f"**На дату {today.isoformat()}:** механически исполняется {mech} "
        f"из {total} обязательных [ОБЯЗ]-правил — **{share}%**.\n\n"
        f"Процессные (ревью/артефакты процесса, признанные ограничения): "
        f"{', '.join(data['process_rules']) or '—'}.\n\n"
        "Формула и обновление: `tools/maturity.py` (запускается при каждом "
        "релизе стандарта; история — `MATURITY_HISTORY.md`).\n",
        encoding="utf-8", newline="\n")

    row = f"| {today.isoformat()} | {mech}/{total} | {share}% |"
    hist = ("# История метрики зрелости (D-3)\n\n"
            "| Дата | Механика / всего [ОБЯЗ] | Доля |\n|---|---|---|\n")
    if HISTORY.exists():
        hist = HISTORY.read_text(encoding="utf-8")
        hist = re.sub(r"\n?$", "\n", hist)
    else:
        hist += "\n"
    if row not in hist:
        hist = hist.rstrip() + "\n" + row + "\n"
    HISTORY.write_text(hist, encoding="utf-8", newline="\n")

    print(f"maturity: {mech}/{total} [ОБЯЗ] механически ({share}%) -> {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
