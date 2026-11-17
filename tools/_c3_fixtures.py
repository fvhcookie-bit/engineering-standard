# Fixtures C-3: Б-9, Б-11…Б-16 (q12/q15/q16) + обновление параметризованного теста.
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tooling" / "fixtures"


def make(name: str, gate: str, base: dict, head: dict, config: dict,
         expect: dict, api: dict | None = None, pr_text: str = "",
         commit_sha: str = "", mode: str = "diff") -> None:
    d = FIXTURES / name
    for sub, tree in (("base", base), ("head", head)):
        for rel, content in tree.items():
            p = d / sub / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8", newline="\n")
    spec: dict = {"gate": gate, "mode": mode, "config": config, "expect": expect}
    if api:
        spec["api"] = api
    if pr_text:
        spec["pr_text"] = pr_text
    if commit_sha:
        spec["commit_sha"] = commit_sha
    (d / "scenario.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")


cfg_q12 = {
    "protected_paths": [
        {"glob": "golden/**", "label": "rule-change", "category": "golden", "oracle": True},
        {"glob": "tests/**", "label": "test-change", "category": "tests"},
        {"glob": "**/tariffs.json", "label": "rule-change", "category": "tariffs"},
    ],
    "code_globs": ["src/**"],
    "q11_config_globs": ["**/tariffs.json"],
}
cfg_q16 = {"task_id": "PROJ-42", "mechanical_globs": [], "line_limit": 600}
cfg_q15 = {
    "success_markers": ["тесты прошли", "tests pass"],
    "known_commands": ["pytest"],
    "pr": 7,
}

# Б-9: ослаблен тест -> test-change + второе ревью
make("b_09", "q12_protected",
     base={"src/app.py": "print(1)\n", "tests/test_x.py": "assert add(1, 1) == 2\n"},
     head={"src/app.py": "print(1)\n", "tests/test_x.py": "# проверка удалена\n"},
     config=cfg_q12,
     expect={"status": "OK", "codes": ["PROTECTED_PATH_TOUCHED"],
             "labels": ["test-change", "second-reviewer-required"]})

# Б-11: новый golden-оракул в одном PR с изменением кода
make("b_11", "q12_protected",
     base={"src/app.py": "print(1)\n"},
     head={"src/app.py": "print(2)\n", "golden/expected.json": '{"out": 2}\n'},
     config=cfg_q12,
     expect={"status": "OK",
             "codes": ["GOLDEN_ORACLE_WITH_CODE", "PROTECTED_PATH_TOUCHED"],
             "labels": ["rule-change", "second-reviewer-required"]})

# Б-12: файл под двумя guard-гейтами (эталон и конфиг) — обе метки, наивысший подписант
make("b_12", "q12_protected",
     base={"golden/tariffs.json": '{"rate": 1}\n'},
     head={"golden/tariffs.json": '{"rate": 2}\n'},
     config=cfg_q12,
     expect={"status": "OK",
             "codes": ["OVERLAP_HIGHEST_SIGNER", "PROTECTED_PATH_TOUCHED"],
             "labels": ["gates-change", "rule-change", "second-reviewer-required"]})

# Б-13: в задаче нет списка файлов -> SKIP с явной причиной
make("b_13", "q16_scope",
     base={"src/a.py": "x = 1\n"},
     head={"src/a.py": "x = 2\n"},
     config=cfg_q16,
     api={"task_files": {"PROJ-42": None}},
     expect={"status": "SKIP", "codes": [], "labels": []})

# Б-14: файл вне списка задачи -> FAIL
make("b_14", "q16_scope",
     base={"src/a.py": "x = 1\n", "src/b.py": "y = 1\n"},
     head={"src/a.py": "x = 2\n", "src/b.py": "y = 2\n"},
     config=cfg_q16,
     api={"task_files": {"PROJ-42": ["src/a.py"]}},
     expect={"status": "FAIL", "codes": ["SCOPE_OUTSIDE_TASK"], "labels": []})

# Б-15: «тесты прошли» при красном конвейере -> FAIL
make("b_15", "q15_verify",
     base={"src/a.py": "x = 1\n"},
     head={"src/a.py": "x = 2\n"},
     config=cfg_q15,
     api={"commit_status": "failure"},
     pr_text="тесты прошли\nстоп-события: нет\n",
     commit_sha="abc123def",
     expect={"status": "FAIL", "codes": ["SUCCESS_MARKER_AT_RED"], "labels": []})

# Б-16: ссылка на чужой прогон + неизвестная команда отсутствует, pytest известен
make("b_16", "q15_verify",
     base={"src/a.py": "x = 1\n"},
     head={"src/a.py": "x = 2\n"},
     config=cfg_q15,
     api={"commit_status": "success", "run_ownership": {"12345": False}},
     pr_text="см. прогон run/12345\n$ pytest\nстоп-события: нет\n",
     commit_sha="abc123def",
     expect={"status": "FAIL", "codes": ["UNKNOWN_RUN_REFERENCE"], "labels": []})

print("fixtures C-3:", len([d for d in FIXTURES.iterdir() if d.name in
      ("b_09", "b_11", "b_12", "b_13", "b_14", "b_15", "b_16")]), "сценариев")

# --- параметризованный тест: api/pr_text/commit_sha из сценария ---
p = ROOT / "tooling" / "tests" / "test_c2_fixtures.py"
t = p.read_text(encoding="utf-8")
old = (
    "    inputs = GateInputs(diff=parse_unified_diff(diff_text), files=files,\n"
    "                        registries=registries, api=FakeAdapter())"
)
new = (
    "    api_spec = spec.get(\"api\", {})\n"
    "    api = FakeAdapter(\n"
    "        commit_status=api_spec.get(\"commit_status\", \"success\"),\n"
    "        run_ownership={int(k): v for k, v in api_spec.get(\"run_ownership\", {}).items()},\n"
    "        task_files={k: v for k, v in api_spec.get(\"task_files\", {}).items()},\n"
    "    )\n"
    "    inputs = GateInputs(diff=parse_unified_diff(diff_text), files=files,\n"
    "                        registries=registries, api=api,\n"
    "                        pr_text=spec.get(\"pr_text\", \"\"),\n"
    "                        commit_sha=spec.get(\"commit_sha\", \"\"))"
)
assert old in t
p.write_text(t.replace(old, new), encoding="utf-8", newline="\n")
print("test loop: api/pr_text подключены")
