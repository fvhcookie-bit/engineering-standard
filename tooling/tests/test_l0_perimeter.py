"""Тесты L0-детектора: здоровый периметр, ослабления, fail-closed, агенты."""



from adapters.base import AdapterUnavailable
from adapters.fake import FakeAdapter
from core.files import RepoFiles
from core.gate_api import GateInputs, Registries
from gates import get_gate

CODEOWNERS_OK = (
    ".github/workflows/ @owner\n"
    "**/pyproject.toml @owner\n"
    "EXCEPTIONS.md @owner\n"
    "REPO_CLASS @owner\n"
    "baseline/ @owner\n"
    "AGENTS.md @owner\n"
    "CODEOWNERS @owner\n"
    "**/.eslintrc* @owner\n"
    "**/eslint.config.* @owner\n"
    "**/.mypy.ini @owner\n"
    "**/setup.cfg @owner\n"
    "**/.clang-tidy @owner\n"
    ".github/PULL_REQUEST_TEMPLATE* @owner\n"
)

PROTECTION_OK = {
    "required_status_checks": {"contexts": ["tooling / tests"]},
    "enforce_admins": {"enabled": True},
    "allow_force_pushes": False,
    "allow_deletions": False,
}


def _gate():
    return get_gate("l0_perimeter")


def _inputs(api: FakeAdapter) -> GateInputs:
    return GateInputs(diff=[], files=RepoFiles(root=None),
                      registries=Registries.empty(), api=api)


def _healthy() -> FakeAdapter:
    return FakeAdapter(branch_protection=PROTECTION_OK, codeowners=CODEOWNERS_OK)


def test_healthy_perimeter_is_ok():
    api = _healthy()
    result = _gate().run(_inputs(api), config={"pr": 0})
    assert result.status.value == "OK"
    assert result.findings == []


def test_branch_not_protected():
    api = _healthy()
    api.branch_protection = None
    result = _gate().run(_inputs(api), config={})
    assert result.status.value == "FAIL"
    assert "BRANCH_NOT_PROTECTED" in {f.code for f in result.findings}


def test_weakened_protection_variants():
    api = _healthy()
    api.branch_protection = {
        "required_status_checks": {"contexts": []},
        "enforce_admins": {"enabled": False},
        "allow_force_pushes": True,
        "allow_deletions": True,
    }
    result = _gate().run(_inputs(api), config={})
    codes = {f.code for f in result.findings}
    assert {"NO_REQUIRED_CHECKS", "FORCE_PUSH_ALLOWED",
            "BRANCH_DELETION_ALLOWED", "ADMIN_BYPASS_NOT_ENFORCED"} <= codes


def test_codeowners_missing():
    api = _healthy()
    api.codeowners = None
    result = _gate().run(_inputs(api), config={})
    assert "CODEOWNERS_MISSING" in {f.code for f in result.findings}


def test_codeowners_no_infra_coverage():
    api = _healthy()
    api.codeowners = "docs/* @someone\n"
    result = _gate().run(_inputs(api), config={})
    codes = [f.code for f in result.findings if f.code == "CODEOWNERS_NO_INFRA_COVERAGE"]
    assert len(codes) >= 5  # workflows, pyproject, EXCEPTIONS, baseline и др.


def test_agent_approval_detected():
    api = _healthy()
    api.reviews[7] = ["human-lead", "helper-bot"]
    result = _gate().run(_inputs(api), config={"pr": 7})
    assert "AGENT_APPROVAL_DETECTED" in {f.code for f in result.findings}


def test_human_review_only_is_fine():
    api = _healthy()
    api.reviews[7] = ["human-lead"]
    result = _gate().run(_inputs(api), config={"pr": 7})
    assert "AGENT_APPROVAL_DETECTED" not in {f.code for f in result.findings}


def test_fail_closed_on_api_unavailable():
    api = _healthy()
    api.protection_unavailable = "GitHub API: 502"
    result = _gate().run(_inputs(api), config={})
    assert result.status.value == "UNAVAILABLE"
    assert "недоступны" in result.reason


def test_adapter_raises_is_unavailable():
    class Broken(FakeAdapter):
        def get_branch_protection(self, branch: str):
            raise AdapterUnavailable("тайм-аут")

    result = _gate().run(_inputs(Broken()), config={})
    assert result.status.value == "UNAVAILABLE"
