"""Тест-контракт словарей подавлений (GUIDELINE_profiles_and_dictionaries §1.2)."""

from pathlib import Path

from core.dictionary import load_dictionary

TOOLING = Path(__file__).resolve().parents[1]
DICTIONARIES = sorted((TOOLING / "dictionaries").glob("*.yaml"))


def _load(path: Path):
    return load_dictionary(path.read_text(encoding="utf-8"))


def test_all_ecosystems_have_dictionary():
    assert len(DICTIONARIES) >= 6, "должны быть словари всех шести стеков"


def test_every_pattern_has_positive_and_negative_fixture():
    for dict_path in DICTIONARIES:
        fix_dir = TOOLING / "dictionaries" / "fixtures" / dict_path.stem
        for p in _load(dict_path):
            positive = (fix_dir / f"{p.id}.positive.txt").read_text(encoding="utf-8")
            negative = (fix_dir / f"{p.id}.negative.txt").read_text(encoding="utf-8")
            assert p.regex.search(positive), f"{dict_path.stem}/{p.id}: позитив не ловится"
            assert not p.regex.search(negative), f"{dict_path.stem}/{p.id}: негатив ложно ловится"


def test_dictionary_schema_and_unique_ids():
    for dict_path in DICTIONARIES:
        patterns = _load(dict_path)
        ids = [p.id for p in patterns]
        assert len(ids) == len(set(ids)), f"{dict_path.name}: дубли id паттернов"
        assert all(p.reason_proximity in ("same_line", "line_above") for p in patterns)
