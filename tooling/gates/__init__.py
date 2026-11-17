"""Реестр гейтов runner'а. Новый гейт регистрируется здесь и получает README."""

from __future__ import annotations

from typing import Any

from gates.demo_dummy.gate import DemoGate
from gates.l0_perimeter.gate import L0PerimeterGate
from gates.q11_suppressions.gate import Q11SuppressionsGate
from gates.q19_audit.gate import Q19AuditGate

GATES: dict[str, Any] = {
    "demo_dummy": DemoGate(),
    "q11_suppressions": Q11SuppressionsGate(),
    "q19_audit": Q19AuditGate(),
    "l0_perimeter": L0PerimeterGate(),
}


def get_gate(name: str) -> Any:
    gate = GATES.get(name)
    if gate is None:
        raise KeyError(f"неизвестный гейт: {name}; доступные: {', '.join(sorted(GATES))}")
    return gate
