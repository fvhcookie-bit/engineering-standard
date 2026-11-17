# Патч C-2: glob-матчер '**/', baseline в base-деревьях, YAML для миграции.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch(rel: str, pairs: list[tuple[str, str]]) -> None:
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert old in t, (rel, old[:70])
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("patched:", rel)


# 1) Q-11: glob_matches вместо fnmatch
patch("tooling/gates/q11_suppressions/gate.py", [
    ("import fnmatch\nimport re", "import re"),
    ("from core.config_fingerprint import detect_tool, fingerprint",
     "from core.config_fingerprint import detect_tool, fingerprint\nfrom core.files import glob_matches"),
    ("fnmatch.fnmatch(", "glob_matches("),
])

# 2) Q-19: то же
patch("tooling/gates/q19_audit/gate.py", [
    ("import fnmatch\nimport re", "import re"),
    ("from core.gate_api import Finding, GateInputs, GateResult, Status",
     "from core.files import glob_matches\nfrom core.gate_api import Finding, GateInputs, GateResult, Status"),
    ("fnmatch.fnmatch(", "glob_matches("),
])

# 3) baseline.py: glob_matches
patch("tooling/core/baseline.py", [
    ("import fnmatch\nfrom typing import Any",
     "from typing import Any"),
    ("from core.dictionary import language_of",
     "from core.dictionary import language_of\nfrom core.files import glob_matches"),
    ("fnmatch.fnmatch(", "glob_matches("),
])

# 4) CLI: миграция пишет YAML (формат гайдлайна), не JSON
patch("tooling/runner/cli.py", [
    ("    new_baseline = migrate(baseline, RepoFiles(root=repo_root), patterns, {}, diff_files)\n"
     "    baseline_path.write_text(\n"
     "        json.dumps(new_baseline, ensure_ascii=False, indent=2) + \"\\n\",\n"
     "        encoding=\"utf-8\", newline=\"\\n\")",
     "    new_baseline = migrate(baseline, RepoFiles(root=repo_root), patterns, {}, diff_files)\n"
     "    import yaml  # type: ignore[import-untyped]\n\n"
     "    baseline_path.write_text(\n"
     "        \"# baseline подавлений (храповик Q-11)\\n\"\n"
     "        + yaml.safe_dump(new_baseline, allow_unicode=True, sort_keys=True),\n"
     "        encoding=\"utf-8\", newline=\"\\n\")"),
])

# 5) fixtures: baseline присутствует уже в base (состояние до PR), кроме Б-7
gen = ROOT / "tools" / "_c2_fixtures.py"
t = gen.read_text(encoding="utf-8")
t = t.replace(
    "make(\"b_01\", \"q11_suppressions\", \"diff\",\n     base={\"src/a.py\": \"x = 1\\n\"},",
    "make(\"b_01\", \"q11_suppressions\", \"diff\",\n"
    "     base={\"src/a.py\": \"x = 1\\n\",\n"
    "           \"baseline/suppressions.yaml\": yaml_baseline({\"noqa\": {\"src/**\": 12}})},")
t = t.replace(
    "make(\"b_02\", \"q11_suppressions\", \"diff\",\n     base={\"src/a.py\": \"pass\\n\"},",
    "make(\"b_02\", \"q11_suppressions\", \"diff\",\n"
    "     base={\"src/a.py\": \"pass\\n\",\n"
    "           \"baseline/suppressions.yaml\": yaml_baseline({\"noqa\": {\"src/**\": 5}})},")
t = t.replace(
    "make(\"b_03\", \"q11_suppressions\", \"diff\",\n     base={\"src/a.py\": \"pass\\n\"},",
    "make(\"b_03\", \"q11_suppressions\", \"diff\",\n"
    "     base={\"src/a.py\": \"pass\\n\",\n"
    "           \"baseline/suppressions.yaml\": yaml_baseline({\"noqa\": {\"src/**\": 5}})},")
t = t.replace(
    "make(\"b_08\", \"q11_suppressions\", \"diff\",\n"
    "     base={\"src/legacy/old.py\": \"# noqa: E501\\n\" * 6},",
    "make(\"b_08\", \"q11_suppressions\", \"diff\",\n"
    "     base={\"src/legacy/old.py\": \"# noqa: E501\\n\" * 6,\n"
    "           \"baseline/suppressions.yaml\": yaml_baseline({\"noqa\": {\"src/legacy/**\": 6}})},")
gen.write_text(t, encoding="utf-8", newline="\n")
print("patched: tools/_c2_fixtures.py (baseline в base)")

# 6) тест Б-10: читать baseline как YAML
patch("tooling/tests/test_b10_migrate.py", [
    ("import json\nfrom pathlib import Path",
     "from pathlib import Path"),
    ("from core.baseline import migrate",
     "from core.baseline import migrate\nfrom core.registries import load_baseline"),
    ("baseline = json.loads((FIXTURE / \"head\" / \"baseline\" / \"suppressions.yaml\").read_text(encoding=\"utf-8\"))",
     "baseline = load_baseline((FIXTURE / \"head\" / \"baseline\" / \"suppressions.yaml\").read_text(encoding=\"utf-8\"))"),
])
