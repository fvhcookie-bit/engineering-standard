"""Словарь подавлений (GUIDELINE_profiles_and_dictionaries §1): загрузка и контракт."""

from __future__ import annotations

import re
from dataclasses import dataclass

PROXIMITIES = ("same_line", "line_above")


@dataclass(frozen=True)
class Pattern:
    """Стабильный id вида подавления — на него ссылается baseline."""

    id: str
    regex: re.Pattern[str]
    languages: tuple[str, ...]
    reason_proximity: str  # same_line | line_above


def load_dictionary(text: str) -> list[Pattern]:
    import yaml  # type: ignore[import-untyped]

    data = yaml.safe_load(text)
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("словарь: schema != 1")
    out: list[Pattern] = []
    default_proximity = data.get("reason_proximity_default", "same_line")
    for p in data["patterns"]:
        proximity = p.get("reason_proximity", default_proximity)
        if proximity not in PROXIMITIES:
            raise ValueError(f"паттерн {p['id']}: недопустимый reason_proximity {proximity!r}")
        out.append(Pattern(
            id=p["id"],
            regex=re.compile(p["regex"]),
            languages=tuple(p.get("languages", [])),
            reason_proximity=proximity,
        ))
    return out


def language_of(path: str, ext_map: dict[str, list[str]]) -> str | None:
    """Язык файла по расширению (маппинг задаётся конфигом гейта)."""
    for lang, exts in ext_map.items():
        for ext in exts:
            if path.endswith(ext):
                return lang
    return None
