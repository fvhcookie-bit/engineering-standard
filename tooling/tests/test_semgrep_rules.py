"""Правила Semgrep Q-17/Q-18: каждый id ловит позитив и не ловит негатив (Б-22/Б-23).

Запуск требует бинарник semgrep; при его отсутствии тесты честно пропускаются
(CI ставит semgrep из requirements-dev; локально на Python >3.11 может не ставиться).
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SEM = Path(__file__).resolve().parents[1] / "semgrep"
SEMGREP_BIN = shutil.which("semgrep")

pytestmark = pytest.mark.skipif(SEMGREP_BIN is None, reason="semgrep не установлен")

PACKS = {
    "q17-timeouts": {"python": {"min_rules": 8}},
    "q18-recursion": {"python": {"min_rules": 4}},
}


def _rule_id(check_id: str) -> str:
    """Semgrep добавляет к check_id префикс пути конфига — берём последний сегмент."""
    return check_id.rsplit(".", 1)[-1]


def _scan(rules: Path, target: Path) -> set[tuple[str, str]]:
    out = subprocess.run(
        [str(SEMGREP_BIN), "--config", str(rules), "--json", "--quiet", str(target)],
        capture_output=True, text=True, check=True, timeout=300,
    )
    data = json.loads(out.stdout)
    return {(_rule_id(r["check_id"]), r["path"]) for r in data.get("results", [])}


def _scan_dir(rules: Path, directory: Path) -> set[tuple[str, str]]:
    out = subprocess.run(
        [str(SEMGREP_BIN), "--config", str(rules), "--json", "--quiet", str(directory)],
        capture_output=True, text=True, check=True, timeout=300,
    )
    data = json.loads(out.stdout)
    return {(_rule_id(r["check_id"]), Path(r["path"]).name)
            for r in data.get("results", [])}


@pytest.mark.parametrize("pack", list(PACKS))
def test_rule_count_and_unique_ids(pack):
    import yaml

    rules = yaml.safe_load((SEM / pack / "python" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    assert len(rules) >= PACKS[pack]["python"]["min_rules"]
    ids = [r["id"] for r in rules]
    assert len(ids) == len(set(ids))
    for r in rules:
        assert r["severity"] == "ERROR"  # К1 — блокирующий режим
        assert r["message"].startswith(("B6/", "A2/", "A3/"))  # трассировка к принципу


@pytest.mark.parametrize("pack", list(PACKS))
def test_positive_and_negative_fixtures(pack):
    """Каждое правило: ловит позитив, не ловит негатив; фиксации трассируются."""
    rules_path = SEM / pack / "python" / "rules.yaml"
    fix_dir = SEM / "fixtures" / pack
    matched = _scan_dir(rules_path, fix_dir)
    import yaml

    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))["rules"]
    for rule in rules:
        rid = rule["id"]
        positives = {p for cid, p in matched if cid == rid
                     and p.startswith("positive_")}
        negatives = {p for cid, p in matched if cid == rid
                     and p.startswith("negative_")}
        assert positives, f"{rid}: позитивный fixture не пойман"
        assert not negatives, f"{rid}: негативный fixture ложно пойман"


def test_b22_http_no_timeout_is_error():
    """Б-22: HTTP-вызов без тайм-аута — ошибка гейта Q-17 (К1)."""
    rules = SEM / "q17-timeouts" / "python" / "rules.yaml"
    matched = _scan_dir(rules, SEM / "fixtures" / "q17-timeouts")
    assert any(cid == "q17-requests-get-no-timeout" for cid, _ in matched)


def test_b23_recursion_without_depth_is_error():
    """Б-23: рекурсия без предела глубины — ошибка гейта Q-18 (К1)."""
    rules = SEM / "q18-recursion" / "python" / "rules.yaml"
    matched = _scan_dir(rules, SEM / "fixtures" / "q18-recursion")
    assert any(cid == "q18-recursion-no-depth" for cid, _ in matched)
