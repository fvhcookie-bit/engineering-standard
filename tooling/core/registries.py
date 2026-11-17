"""Парсеры реестров целевого репозитория: EXCEPTIONS.md, baseline, REPO_CLASS, CODEOWNERS.

Источники истины гейтов (GUIDELINE_development §2): гейт читает эти файлы и API —
никогда не описание PR.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

EX_ID_RE = r"^###\s+(EX-\d{4}-\d{3})\s*$"


@dataclass
class ExEntry:
    """Запись реестра E-C (EXCEPTIONS_POLICY §3)."""

    id: str
    principle: str = ""
    scope: str = ""
    reason: str = ""
    compensation: str = ""
    signer: str = ""
    review_due: date | None = None
    status: str = ""

    def is_expired(self, today: date | None = None) -> bool:
        today = today or date.today()
        return self.review_due is not None and self.review_due < today


_FIELD_MAP = {
    "Принцип": "principle",
    "Область": "scope",
    "Суть отступления": "reason",
    "Обоснование": "rationale",
    "Компенсирующие меры": "compensation",
    "Подписант": "signer",
    "Срок пересмотра": "review_due",
    "Статус": "status",
}


def _parse_date(value: str) -> date | None:
    value = value.strip()
    parts = value.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        try:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return None
    return None


def parse_exceptions_md(text: str) -> list[ExEntry]:
    """Блоки '### EX-ГГГГ-NNN' с полями '- **Поле:** значение' (EXCEPTIONS_POLICY §3)."""
    out: list[ExEntry] = []
    current: ExEntry | None = None
    for raw in text.splitlines():
        line = raw.strip()
        marker = line[4:].strip() if line.startswith("### ") else ""
        if marker and marker.startswith("EX-"):
            current = ExEntry(id=marker)
            out.append(current)
            continue
        if current is None or not line.startswith("- **"):
            continue
        body = line[4:]  # содержимое после '- **'
        end = body.find("**")
        if end == -1:
            continue
        name = body[:end].strip().rstrip(":")
        rest = body[end + 2:].strip()
        rest = rest.removeprefix(":")
        value = rest.strip()
        attr = _FIELD_MAP.get(name)
        if attr is None:
            continue
        if attr == "review_due":
            setattr(current, attr, _parse_date(value))
        else:
            setattr(current, attr, value)
    return out


@dataclass
class Registries:
    """Реестры целевого репозитория, поданные гейту как явный вход."""

    exceptions: list[ExEntry] = field(default_factory=list)
    baseline: dict[str, Any] = field(default_factory=dict)
    repo_class: dict[str, str] = field(default_factory=dict)
    codeowners: list[tuple[str, list[str]]] = field(default_factory=list)

    @classmethod
    def empty(cls) -> Registries:
        return cls()

    @classmethod
    def from_repo(cls, root: Path) -> Registries:
        """Загрузка стандартных реестров целевого репозитория (TASK §2)."""
        from core.files import RepoFiles

        rf = RepoFiles(root=root)
        exc = rf.read("EXCEPTIONS.md")
        rc = rf.read("REPO_CLASS")
        bl = rf.read("baseline/suppressions.yaml")
        co = rf.read("CODEOWNERS")
        return cls(
            exceptions=parse_exceptions_md(exc) if exc else [],
            baseline=load_baseline(bl) if bl else {},
            repo_class=parse_repo_class(rc) if rc else {},
            codeowners=parse_codeowners(co) if co else [],
        )

    def exception_by_id(self, ex_id: str) -> ExEntry | None:
        for e in self.exceptions:
            if e.id == ex_id:
                return e
        return None


def load_baseline(text: str) -> dict[str, Any]:
    import yaml  # type: ignore[import-untyped]

    data = yaml.safe_load(text)
    return data if isinstance(data, dict) else {}


def parse_repo_class(text: str) -> dict[str, str]:
    """Строки 'ключ = значение' или 'ключ: значение' — классы и версия стандарта."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        for sep in ("=", ":"):
            if sep in line:
                k, v = line.split(sep, 1)
                out[k.strip()] = v.strip()
                break
    return out


def parse_codeowners(text: str) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            out.append((parts[0], parts[1:]))
    return out
