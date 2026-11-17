# Генератор fixtures и артефактов C-2: словарь, контракты, сценарии Б-1…Б-20.
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tooling"))

from core.config_fingerprint import fingerprint  # noqa: E402

DICT_DIR = ROOT / "tooling" / "dictionaries"
FIXTURES = ROOT / "tooling" / "fixtures"

DICT_YAML = """schema: 1
ecosystem: python
reason_proximity_default: same_line
patterns:
  - id: noqa
    regex: '#\\s*noqa(?::\\s*[A-Z0-9, ]+)?'
    languages: [python]
  - id: type_ignore
    regex: '#\\s*type:\\s*ignore'
    languages: [python]
  - id: pyright_ignore
    regex: '#\\s*pyright:\\s*ignore'
    languages: [python]
  - id: pytest_skip
    regex: '@pytest\\.mark\\.(skip|skipif|xfail)\\b'
    languages: [python]
  - id: unittest_skip
    regex: '@unittest\\.skip(If|Unless)?\\('
    languages: [python]
  - id: cast_any
    regex: '\\bcast\\(\\s*Any\\b'
    languages: [python]
  - id: mypy_ignore_errors
    regex: 'ignore_errors\\s*=\\s*True'
    languages: [python]
"""

POSITIVE = {
    "noqa": "x = 1  # noqa: E501",
    "type_ignore": "x = call()  # type: ignore",
    "pyright_ignore": "x = call()  # pyright: ignore[reportGeneralTypeIssues]",
    "pytest_skip": "@pytest.mark.skip(reason=\"env\")",
    "unittest_skip": "@unittest.skipIf(sys.platform == 'win32', 'env')",
    "cast_any": "value = cast(Any, payload)",
    "mypy_ignore_errors": "[tool.mypy.scripts.legacy]\nignore_errors = True",
}
NEGATIVE = {
    "noqa": "x = 1  # обычный комментарий",
    "type_ignore": "x = call()  # обычный комментарий",
    "pyright_ignore": "x = call()  # обычный комментарий",
    "pytest_skip": "@pytest.mark.parametrize(\"v\", [1])",
    "unittest_skip": "@unittest.TestCase class — не декоратор",
    "cast_any": "value = cast(int, payload)",
    "mypy_ignore_errors": "ignore_errors = False",
}


def w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


# --- словарь + контракты ---
w(DICT_DIR / "python.yaml", DICT_YAML)
fx = DICT_DIR / "fixtures" / "python"
for pid, pos in POSITIVE.items():
    w(fx / f"{pid}.positive.txt", pos + "\n")
    w(fx / f"{pid}.negative.txt", NEGATIVE[pid] + "\n")
print("словарь python.yaml + контракты:", len(POSITIVE), "паттернов")

EMPTY_BASELINE = json.dumps({
    "schema": 1, "counts": {}, "fingerprint": {},
    "generated_by": "gate-runner init",
}, ensure_ascii=False, indent=2) + "\n"

EXCEPTIONS_EMPTY = "# Реестр исключений E-C (EXCEPTIONS_POLICY §3)\n"

# --- сценарии Б ---
def make(name: str, gate: str, mode: str, base: dict, head: dict,
         config: dict, expect: dict, extra: dict | None = None) -> None:
    d = FIXTURES / name
    for sub, tree in (("base", base), ("head", head)):
        for rel, content in tree.items():
            w(d / sub / rel, content)
    spec = {"gate": gate, "mode": mode, "config": config, "expect": expect}
    if extra:
        spec["extra"] = extra
        for rel, content in extra.get("files", {}).items():
            w(d / rel, content)
    w(d / "scenario.json", json.dumps(spec, ensure_ascii=False, indent=2) + "\n")


def yaml_baseline(counts: dict) -> str:
    import yaml  # noqa
    return "# baseline подавлений (храповик Q-11)\n" + yaml.safe_dump(
        {"schema": 1, "counts": counts, "fingerprint": {},
         "generated_by": "gate-runner init"}, allow_unicode=True, sort_keys=True)


cfg_q11 = {
    "dictionary": "tooling/dictionaries/python.yaml",
    "language_ext": {"python": [".py"]},
    "config_files": ["**/.eslintrc.json", "**/eslint.config.json",
                     "**/pyproject.toml", "**/.mypy.ini", "**/setup.cfg",
                     "**/.github/workflows/*.yml"],
    "baseline_paths": ["baseline/**", "dictionaries/**"],
}

# Б-1: 30 подавлений без EX, baseline 12; в PR заявлено «30» — гейт декларации не видит
noqa30 = "\n".join("# noqa: E501" for _ in range(30))
make("b_01", "q11_suppressions", "diff",
     base={"src/a.py": "x = 1\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 12}})},
     head={"src/a.py": "x = 1\n" + noqa30 + "\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 12}})},
     config=cfg_q11,
     expect={"status": "FAIL",
             "codes": ["BASELINE_GROWTH", "SUPPRESS_NO_EXID"],
             "labels": ["second-reviewer-required"]},
     extra={"files": {"pr_description.md": "мы добавили 30 подавлений: 30\n"}})

# Б-2: подавление без причины и EX-ID (в baseline есть запас)
make("b_02", "q11_suppressions", "diff",
     base={"src/a.py": "pass\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 5}})},
     head={"src/a.py": "pass\n# noqa: E501\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 5}})},
     config=cfg_q11,
     expect={"status": "FAIL", "codes": ["SUPPRESS_NO_EXID"], "labels": []})

# Б-3: чужой EX-ID и истёкший EX-ID
EXC_B3 = ("# Реестр исключений E-C\n\n### EX-2026-001\n"
          "- **Принцип:** B6\n- **Область:** src/legacy\n"
          "- **Суть отступления:** лимит задан протоколом\n"
          "- **Компенсирующие меры:** watchdog\n- **Подписант:** tech lead\n"
          "- **Срок пересмотра:** 2026-01-01\n- **Статус:** активное\n")
make("b_03", "q11_suppressions", "diff",
     base={"src/a.py": "pass\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 5}})},
     head={"src/a.py": ("pass\n# noqa: E501  # EX-2026-099: чужой\n"
                        "# noqa: E501  # EX-2026-001: истёк\n"),
           "EXCEPTIONS.md": EXC_B3,
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 5}})},
     config=cfg_q11,
     expect={"status": "FAIL",
             "codes": ["SUPPRESS_UNKNOWN_EXID", "SUPPRESS_EXID_EXPIRED"],
             "labels": []})

# Б-4: изменён CI-workflow -> gates-change
make("b_04", "q11_suppressions", "diff",
     base={"src/a.py": "pass\n"},
     head={"src/a.py": "pass\n", ".github/workflows/ci.yml": "jobs: {}\n"},
     config=cfg_q11,
     expect={"status": "OK", "codes": ["CONFIG_FILE_TOUCHED"], "labels": ["gates-change"]})

# Б-5: вложенный .eslintrc в подкаталоге -> gates-change
make("b_05", "q11_suppressions", "diff",
     base={"src/a.py": "pass\n"},
     head={"src/a.py": "pass\n", "sub/.eslintrc.json": "{\"rules\": {}}\n"},
     config=cfg_q11,
     expect={"status": "OK", "codes": ["CONFIG_FILE_TOUCHED"], "labels": ["gates-change"]})

# Б-6: изменён порог внутри существующего конфига -> fingerprint -> gates-change
base_pyproject = '[tool.ruff]\nselect = ["E"]\n'
head_pyproject = '[tool.ruff]\nselect = ["E", "W"]\n'
fp_base = fingerprint(base_pyproject, "ruff")
baseline_b6 = {"schema": 1, "counts": {}, "fingerprint": {"ruff": {"pyproject.toml": fp_base}},
               "generated_by": "gate-runner init"}
make("b_06", "q11_suppressions", "diff",
     base={"pyproject.toml": base_pyproject,
           "baseline/suppressions.yaml": json.dumps(baseline_b6, ensure_ascii=False, indent=2) + chr(10)},
     head={"pyproject.toml": head_pyproject,
           "baseline/suppressions.yaml": json.dumps(baseline_b6, ensure_ascii=False, indent=2) + "\n"},
     config=cfg_q11,
     expect={"status": "OK", "codes": ["CONFIG_FILE_TOUCHED", "CONFIG_FINGERPRINT_CHANGED"],
             "labels": ["gates-change"]})

# Б-7: baseline + код в одном PR
make("b_07", "q11_suppressions", "diff",
     base={"src/a.py": "x = 1\n# noqa: E501\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 2}})},
     head={"src/a.py": "x = 1\n",
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/**": 0}})},
     config=cfg_q11,
     expect={"status": "FAIL", "codes": ["BASELINE_WITH_CODE"], "labels": []})

# Б-8: -2 старых / +3 новых — компенсация запрещена
make("b_08", "q11_suppressions", "diff",
     base={"src/legacy/old.py": "# noqa: E501\n" * 6,
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/legacy/**": 6}})},
     head={"src/legacy/old.py": "# noqa: E501\n" * 4,
           "src/new.py": ("total = compute_total(items)  # noqa: E501\n"
                              "cache = build_cache(data)  # noqa: E501\n"
                              "log = setup_logging()  # noqa: E501\n"),
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/legacy/**": 6}})},
     config=cfg_q11,
     expect={"status": "FAIL", "codes": ["BASELINE_GROWTH", "SUPPRESS_NO_EXID"], "labels": []})

# Б-10: rename модуля с переносом подавлений — миграция инструментом (см. test_b10)
make("b_10", "q11_suppressions", "diff",
     base={"src/legacy/app.py": "# noqa: E501\n" * 6},
     head={"src/legacy/app2.py": "# noqa: E501\n" * 6,
           "baseline/suppressions.yaml": yaml_baseline({"noqa": {"src/legacy/**": 6}})},
     config=cfg_q11,
     expect={"status": "OK", "codes": [], "labels": []})

# --- Q-19 (tree-режим) ---
cfg_q19 = {"today": "2026-11-17", "k3_limit": 0.2, "k3_alert": 0.16}

# Б-17: якорь EX без записи в реестре
make("b_17", "q19_audit", "tree",
     base={},
     head={"src/x.py": "clean()\n# EX-2026-042: причина\n",
           "EXCEPTIONS.md": EXCEPTIONS_EMPTY},
     config=cfg_q19,
     expect={"status": "FAIL", "codes": ["ANCHOR_WITHOUT_ENTRY"], "labels": []})

# Б-18: 3+ исключения одного принципа/причины -> автозадача E-D
exc_b18 = EXCEPTIONS_EMPTY + "".join(
    f"### EX-2026-00{i}\n- **Принцип:** B6\n- **Область:** src/{i}\n"
    "- **Суть отступления:** лимит задан протоколом v1\n"
    "- **Компенсирующие меры:** watchdog\n- **Подписант:** tech lead\n"
    f"- **Срок пересмотра:** 2027-06-01\n- **Статус:** активное\n\n"
    for i in (1, 2, 3))
make("b_18", "q19_audit", "tree",
     base={},
     head={"src/one.py": "# EX-2026-001\n", "src/two.py": "# EX-2026-002\n",
           "src/three.py": "# EX-2026-003\n", "EXCEPTIONS.md": exc_b18},
     config=cfg_q19,
     expect={"status": "OK", "codes": ["AUTO_TASK_ED"], "labels": []})

# Б-19: просроченное исключение -> FAIL по затронутому файлу
exc_b19 = (EXCEPTIONS_EMPTY + "### EX-2026-001\n- **Принцип:** B6\n- **Область:** src/a\n"
           "- **Суть отступления:** причина\n- **Компенсирующие меры:** контроль\n"
           "- **Подписант:** tech lead\n- **Срок пересмотра:** 2026-01-01\n- **Статус:** активное\n")
make("b_19", "q19_audit", "tree",
     base={},
     head={"src/a.py": "recv()\n# EX-2026-001\n", "EXCEPTIONS.md": exc_b19},
     config=cfg_q19,
     expect={"status": "FAIL", "codes": ["EXPIRED_EXCEPTION"], "labels": []})

# Б-20: доля К3 выросла до порога алерта (2/11 ≈ 18% >= 16%)
head_b20 = {"src/a.py": "", "src/b.py": "", "src/c.py": "", "src/d.py": "",
            "src/e.py": "", "src/f.py": "", "src/g.py": "", "src/h.py": "",
            "src/i.py": "", "exp/x.py": "", "exp/y.py": ""}
make("b_20", "q19_audit", "tree",
     base={},
     head={**head_b20, "REPO_CLASS": "k3_globs = exp/**\nversion = 1.2\n"},
     config=cfg_q19,
     expect={"status": "OK", "codes": ["K3_LIMIT_ALERT"], "labels": []})

print("fixtures:", len(list(FIXTURES.glob('b_*'))), "сценариев; словарные контракты: 14 файлов")
