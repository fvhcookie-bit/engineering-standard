"""D-3: метрика зрелости считается по итоговой таблице EP и публикуется.

Импорт сверху: conftest добавляет каталог tools/ в sys.path до загрузки
тестовых модулей — подавления импорта не требуются (Q-11 самогейт).
"""

import re
from pathlib import Path

from maturity import compute

ROOT = Path(__file__).resolve().parents[2]


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
