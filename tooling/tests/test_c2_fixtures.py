"""Матрица приёмочных сценариев Б (fixtures/<сценарий> + expected.json, гайдлайн §7.1)."""

import json
from pathlib import Path

import pytest
from adapters.fake import FakeAdapter
from core.diff import parse_unified_diff
from core.files import RepoFiles
from core.gate_api import GateInputs
from core.registries import Registries
from gates import get_gate
from harness import make_diff

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SCENARIOS = sorted(p for p in FIXTURES.iterdir() if p.is_dir() and p.name.startswith("b_"))


def _tree(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
        for p in root.rglob("*") if p.is_file()
    }


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda p: p.name)
def test_acceptance_scenario(scenario: Path, tmp_path: Path):
    spec = json.loads((scenario / "scenario.json").read_text(encoding="utf-8"))
    base_root = scenario / "base"
    head_root = scenario / "head"
    base = _tree(base_root) if base_root.is_dir() else {}
    head = _tree(head_root)

    if spec["mode"] == "tree":
        for rel, content in head.items():
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        diff_text = ""
        files = RepoFiles(root=tmp_path)
        registries = Registries.from_repo(tmp_path)
    else:
        diff_text = make_diff(base, head)
        for rel, content in head.items():
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        files = RepoFiles(root=tmp_path)
        registries = Registries.from_repo(tmp_path)

    cfg = dict(spec.get("config", {}))
    if "dictionary" in cfg:
        from core.dictionary import load_dictionary

        candidates = [FIXTURES.parent / cfg["dictionary"], FIXTURES.parent.parent / cfg["dictionary"]]
        dict_path = next(p for p in candidates if p.is_file())
        cfg["patterns"] = load_dictionary(dict_path.read_text(encoding="utf-8"))

    inputs = GateInputs(diff=parse_unified_diff(diff_text), files=files,
                        registries=registries, api=FakeAdapter())
    result = get_gate(spec["gate"]).run(inputs, config=cfg)

    expect = spec["expect"]
    assert result.status.value == expect["status"], (
        f"{scenario.name}: статус {result.status.value}, коды "
        f"{sorted({f.code for f in result.findings})}"
    )
    assert sorted({f.code for f in result.findings}) == sorted(expect["codes"]), (
        f"{scenario.name}: расхождение кодов findings"
    )
    assert sorted(set(result.labels)) == sorted(expect["labels"]), (
        f"{scenario.name}: расхождение меток"
    )


def test_b1_declaration_is_never_an_input():
    """Анти-самоотчётность (Б-1): декларация PR существует в fixture, но не попадает в гейт."""
    scenario = FIXTURES / "b_01"
    declaration = (scenario / "pr_description.md").read_text(encoding="utf-8")
    assert "30" in declaration
    # GateInputs не содержит поля для деклараций — структурная невозможность
    from core.gate_api import GateInputs

    assert not hasattr(GateInputs, "pr_description")
    assert "pr_description" not in GateInputs.__dataclass_fields__
