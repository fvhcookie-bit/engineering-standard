"""D-3: метрика зрелости — доля [ОБЯЗ]-правил, исполняемых механикой.

Формула: из итоговой таблицы ENGINEERING_PRINCIPLES считаются правила класса
[ОБЯЗ]; правила с пометкой «процессное» в колонке гейта исполняются
ревью/артефактами процесса, остальные — механикой (гейты/CI).
Публикуется в корне репозитория (MATURITY.md) с историей по датам
(MATURITY_HISTORY.md) — тренд виден между релизами.

Защита от молчаливой деградации: если итоговая таблица не распознана
(0 строк), скрипт завершается ошибкой и ничего не публикует.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "standards" / "ENGINEERING_PRINCIPLES.md"
OUT = ROOT / "MATURITY.md"
HISTORY = ROOT / "MATURITY_HISTORY.md"

ROW = re.compile(r"^\| ([A-H]\d) \| (.+?) \| ([А-ЯЁ]{4}(?:\s*\(.+?\))?) \| (.+?) \|$")
DATE_ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|")

HISTORY_HEADER = ("# История метрики зрелости (D-3)\n\n"
                  "| Дата | Механика / всего [ОБЯЗ] | Доля |\n|---|---|---|\n")


def compute(ep_text: str | None = None) -> dict[str, object]:
    text = ep_text if ep_text is not None else EP.read_text(encoding="utf-8")
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


def update_history(hist_text: str, row: str) -> str:
    """Добавляет строку истории; строка той же даты заменяется, не дублируется."""
    m = DATE_ROW.match(row)
    day = m.group(1) if m else ""
    kept = [ln for ln in hist_text.rstrip().splitlines()
            if not (day and (dm := DATE_ROW.match(ln)) and dm.group(1) == day)]
    return "\n".join(kept + [row]) + "\n"


def main(argv: list[str] | None = None, *, ep: Path = EP, out: Path = OUT,
         history: Path = HISTORY) -> int:
    args = argv if argv is not None else sys.argv[1:]
    today = date.fromisoformat(args[0]) if args else date.today()
    data = compute(ep.read_text(encoding="utf-8"))
    total = data["obyaz_total"]
    mech = data["obyaz_mechanical"]
    share = data["share_percent"]
    if total == 0:
        print("ошибка: итоговая таблица EP не распознана — метрика не публикуется",
              file=sys.stderr)
        return 1

    rules = ", ".join(data["process_rules"]) or "—"
    out.write_text(
        "# Метрика зрелости стандарта (D-3)\n\n"
        f"**На дату {today.isoformat()}:** механически исполняется {mech} "
        f"из {total} обязательных [ОБЯЗ]-правил — **{share}%**.\n\n"
        f"Процессные (ревью/артефакты процесса, признанные ограничения): {rules}.\n\n"
        "Формула и обновление: `tools/maturity.py` (запускается при каждом "
        "релизе стандарта; история — `MATURITY_HISTORY.md`).\n",
        encoding="utf-8", newline="\n")

    row = f"| {today.isoformat()} | {mech}/{total} | {share}% |"
    hist = history.read_text(encoding="utf-8") if history.exists() else HISTORY_HEADER
    history.write_text(update_history(hist, row), encoding="utf-8", newline="\n")

    print(f"maturity: {mech}/{total} [ОБЯЗ] механически ({share}%) -> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
