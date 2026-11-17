"""Config-fingerprint (GUIDELINE_profiles_and_dictionaries §2).

Канонический JSON эффективной конфигурации -> SHA-256. Изменение fingerprint
или появление нового конфиг-файла инструмента -> метка gates-change (Q-11).
"""

from __future__ import annotations

import configparser
import hashlib
import json
import tomllib
from pathlib import PurePosixPath

_TOOL_BY_NAME = {
    ".eslintrc.json": "eslint_json",
    "eslint.config.json": "eslint_json",
    "pyproject.toml": "ruff",
    ".mypy.ini": "mypy",
    "mypy.ini": "mypy",
    "setup.cfg": "mypy",
}


def detect_tool(path: str) -> str | None:
    name = PurePosixPath(path).name
    return _TOOL_BY_NAME.get(name)


def _canonical(obj: object) -> object:
    if isinstance(obj, dict):
        return {k: _canonical(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [_canonical(x) for x in obj]
    return obj


def parse_canonical(text: str, tool: str) -> object:
    """Каноническое представление эффективной конфигурации."""
    if tool == "eslint_json":
        return json.loads(text)
    if tool == "ruff":
        data = tomllib.loads(text)
        return _canonical(data.get("tool", {}).get("ruff", data))
    if tool == "mypy":
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(text)
        return _canonical({s: dict(parser.items(s)) for s in parser.sections()})
    raise ValueError(f"нет парсера для инструмента {tool!r}")


def fingerprint(text: str, tool: str) -> str | None:
    try:
        canonical = parse_canonical(text, tool)
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, configparser.Error):
        return None  # неразбираемый конфиг — не молчаливый OK: гейт помечает ограничение
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
