"""Тест-контракт словаря подавлений (GUIDELINE_profiles_and_dictionaries §1.2)."""

from pathlib import Path

from core.dictionary import load_dictionary

TOOLING = Path(__file__).resolve().parents[1]


def test_every_pattern_has_positive_and_negative_fixture():
    patterns = load_dictionary((TOOLING / "dictionaries" / "python.yaml").read_text(encoding="utf-8"))
    assert len(patterns) >= 5, "словарь не должен быть пустым"
    fix_dir = TOOLING / "dictionaries" / "fixtures" / "python"
    for p in patterns:
        positive = (fix_dir / f"{p.id}.positive.txt").read_text(encoding="utf-8")
        negative = (fix_dir / f"{p.id}.negative.txt").read_text(encoding="utf-8")
        assert p.regex.search(positive), f"{p.id}: позитивный fixture не ловится"
        assert not p.regex.search(negative), f"{p.id}: негативный fixture ложно ловится"


def test_dictionary_schema_and_proximity():
    patterns = load_dictionary((TOOLING / "dictionaries" / "python.yaml").read_text(encoding="utf-8"))
    ids = [p.id for p in patterns]
    assert len(ids) == len(set(ids)), "дубли id паттернов"
    assert all(p.reason_proximity in ("same_line", "line_above") for p in patterns)
