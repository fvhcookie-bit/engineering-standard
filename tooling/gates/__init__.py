"""Реестр гейтов runner'а. Новый гейт регистрируется здесь и получает README."""

from __future__ import annotations

from typing import Any

from gates.demo_dummy.gate import DemoGate

GATES: dict[str, Any] = {
    "demo_dummy": DemoGate(),
}


def get_gate(name: str) -> Any:
    gate = GATES.get(name)
    if gate is None:
        raise KeyError(f"неизвестный гейт: {name}; доступные: {', '.join(sorted(GATES))}")
    return gate
