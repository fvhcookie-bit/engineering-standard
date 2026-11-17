"""L0-детектор «Периметр репозитория» (QUALITY_GATES §1.5, TASK C-4).

Проверяет, что механическое принуждение нельзя выключить изнутри:
- защита основной ветки: запрет push, force-push, удаления; обязательные проверки;
- CODEOWNERS существует и покрывает инфраструктуру стандарта (защищённые пути);
- одобрения PR — только люди (ИИ-помощник не может ревьюить);
- обход админа либо запрещён, либо оформлен как процессное отступление.

Fail-closed: данные о защите недоступны -> UNAVAILABLE (красный), не «молчаливый OK».
Гейт работает через Adapter API (нужен токен с правами админа — см. README).
"""

from __future__ import annotations

import fnmatch
from typing import Any

from adapters.base import AdapterUnavailable
from core.files import glob_matches
from core.gate_api import Finding, GateInputs, GateResult, Status
from core.registries import parse_codeowners

GATE_ID = "L0-01"
GATE_VERSION = "1.0.0"

DEFAULT_INFRA_PATHS = [
    ".github/workflows/**",
    "**/.eslintrc*", "**/eslint.config.*", "**/pyproject.toml",
    "**/.mypy.ini", "**/setup.cfg", "**/.clang-tidy",
    "EXCEPTIONS.md", "REPO_CLASS", "baseline/**",
    "AGENTS.md", "CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE*",
]
DEFAULT_AGENT_PATTERNS = ["*-bot", "bot-*", "*[bot]", "dependabot[bot]"]


def _is_agent_login(login: str, patterns: list[str]) -> bool:
    lowered = login.lower()
    return any(fnmatch.fnmatch(lowered, p.lower()) for p in patterns)


class L0PerimeterGate:
    id = GATE_ID
    version = GATE_VERSION

    def run(self, inputs: GateInputs, config: dict[str, Any]) -> GateResult:
        result = GateResult(gate_id=GATE_ID, gate_version=GATE_VERSION, status=Status.OK)
        branch = str(config.get("branch", "main"))
        infra_paths: list[str] = config.get("infra_paths", DEFAULT_INFRA_PATHS)
        agent_patterns: list[str] = config.get("agent_login_patterns", DEFAULT_AGENT_PATTERNS)
        pr_number = int(config.get("pr", 0))

        # Fail-closed: любые проблемы API -> UNAVAILABLE
        try:
            protection = inputs.api.get_branch_protection(branch)
            codeowners_text = inputs.api.get_codeowners()
            reviewers = inputs.api.list_review_logins(pr_number) if pr_number else []
        except AdapterUnavailable as exc:
            result.status = Status.UNAVAILABLE
            result.reason = f"данные о периметре недоступны: {exc}"
            return result.finalize()

        # 1. Защита основной ветки
        if protection is None:
            result.findings.append(Finding(
                code="BRANCH_NOT_PROTECTED", severity="error",
                path=branch, line=0,
                message=(f"ветка {branch} не защищена: прямой push, force-push и "
                         "удаление не запрещены; обязательные проверки не заданы"),
            ))
        else:
            checks = protection.get("required_status_checks")
            if not checks or not checks.get("contexts"):
                result.findings.append(Finding(
                    code="NO_REQUIRED_CHECKS", severity="error",
                    path=branch, line=0,
                    message="обязательные проверки (required status checks) не заданы",
                ))
            enforcement = protection.get("enforce_admins")
            if isinstance(enforcement, dict) and not enforcement.get("enabled"):
                result.findings.append(Finding(
                    code="ADMIN_BYPASS_NOT_ENFORCED", severity="warning",
                    path=branch, line=0,
                    message=("правила защиты не распространяются на администраторов — "
                             "оформить как процессное отступление либо включить enforce"),
                ))
            if protection.get("allow_force_pushes"):
                result.findings.append(Finding(
                    code="FORCE_PUSH_ALLOWED", severity="error",
                    path=branch, line=0,
                    message="force-push в защищённую ветку разрешён",
                ))
            if protection.get("allow_deletions"):
                result.findings.append(Finding(
                    code="BRANCH_DELETION_ALLOWED", severity="error",
                    path=branch, line=0,
                    message="удаление защищённой ветки разрешено",
                ))

        # 2. CODEOWNERS: существует и покрывает инфраструктуру
        if codeowners_text is None:
            result.findings.append(Finding(
                code="CODEOWNERS_MISSING", severity="error",
                path="CODEOWNERS", line=0,
                message="файл CODEOWNERS не найден (.github/, корень или docs/)",
            ))
        else:
            owners = parse_codeowners(codeowners_text)
            if not owners:
                result.findings.append(Finding(
                    code="CODEOWNERS_EMPTY", severity="error",
                    path="CODEOWNERS", line=0,
                    message="CODEOWNERS пуст — защищённые пути не назначены",
                ))
            for infra in infra_paths:
                covered = any(glob_matches(infra, pattern) or glob_matches(pattern, infra)
                              for pattern, _ in owners)
                if not covered:
                    result.findings.append(Finding(
                        code="CODEOWNERS_NO_INFRA_COVERAGE", severity="error",
                        path="CODEOWNERS", line=0,
                        message=f"защищённый путь не покрыт CODEOWNERS: {infra}",
                    ))

        # 3. Одобрения — только люди (при переданном PR)
        for login in reviewers:
            if _is_agent_login(login, agent_patterns):
                result.findings.append(Finding(
                    code="AGENT_APPROVAL_DETECTED", severity="error",
                    path=login, line=0,
                    message="одобрение PR от ИИ-агента запрещено (ревью — только человек)",
                ))

        result.stats = {
            "branch": branch,
            "infra_paths_checked": len(infra_paths),
            "reviewers_checked": len(reviewers),
        }
        return result.finalize()
