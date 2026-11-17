"""D-3: метрика зрелости — compute, дедупликация истории, публикация main()."""

import re
from pathlib import Path

from maturity import compute, main, update_history

ROOT = Path(__file__).resolve().parents[2]

EP_SAMPLE = (
    "| A1 | Правило | ОБЯЗ | линт |\n"
    "| H1 | Процесс | ОБЯЗ | процессное |\n"
)


def test_compute_counts_match_table():
    ep = (ROOT / "standards" / "ENGINEERING_PRINCIPLES.md").read_text(encoding="utf-8")
    table_rows = [ln for ln in ep.splitlines()
                  if re.match(r"^\| [A-H]\d \| .+ \| (ОБЯЗ|РЕК|УСЛ)", ln)]
    obyaz = [ln for ln in table_rows if " ОБЯЗ |" in ln]
    data = compute(ep)
    assert data["obyaz_total"] == len(obyaz) == data["obyaz_mechanical"] + data["obyaz_process"]
    assert 0 <= data["share_percent"] <= 100


def test_process_rules_are_reported():
    data = compute()
    # v1.2: процессные [ОБЯЗ]-правила — H1/H2/H5/H7/H9 (частично) и др. пометки
    assert data["obyaz_process"] >= 1
    assert len(data["process_rules"]) == data["obyaz_process"]


def test_update_history_replaces_same_date_row():
    hist = ("# История\n\n| Дата | X | Y |\n|---|---|---|\n"
            "| 2026-11-18 | 1/2 | 50% |\n")
    updated = update_history(hist, "| 2026-11-18 | 2/2 | 100% |")
    assert updated.count("| 2026-11-18 |") == 1
    assert "100%" in updated
    two_days = update_history(updated, "| 2026-11-19 | 2/2 | 100% |")
    assert two_days.count("| 2026-11-") == 2


def test_main_unrecognized_table_fails_without_publishing(tmp_path):
    ep = tmp_path / "EP.md"
    ep.write_text("нет таблицы\n", encoding="utf-8", newline="\n")
    code = main(argv=["2026-11-18"], ep=ep,
                out=tmp_path / "M.md", history=tmp_path / "H.md")
    assert code == 1
    assert not (tmp_path / "M.md").exists()
    assert not (tmp_path / "H.md").exists()


def test_main_full_cycle_and_same_date_dedup(tmp_path):
    ep = tmp_path / "EP.md"
    ep.write_text(EP_SAMPLE, encoding="utf-8", newline="\n")
    out, hist = tmp_path / "M.md", tmp_path / "H.md"
    assert main(argv=["2026-11-17"], ep=ep, out=out, history=hist) == 0
    # повторный запуск за ту же дату — замена строки, не дубль
    assert main(argv=["2026-11-17"], ep=ep, out=out, history=hist) == 0
    text = hist.read_text(encoding="utf-8")
    assert text.count("| 2026-11-17 |") == 1
    assert "1/2" in text
    published = out.read_text(encoding="utf-8")
    assert "**50%**" in published
    assert "H1" in published
