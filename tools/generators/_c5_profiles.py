# Профили строгих конфигураций для 6 стеков (GUIDELINE_profiles_and_dictionaries §3).
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILES = ROOT / "tooling" / "profiles"


def w(rel: str, text: str) -> None:
    p = PROFILES / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


w("python/ruff.toml", """# Профиль стандарта v1.2: максимальная строгость для Python.
# Отключения — только с комментарием-причиной (проходит через Q-11 companion).
line-length = 100

[lint]
select = ["ALL"]
ignore = [
    # причина: конфликтуют между собой и с чёрным форматированием
    "COM812", "ISC001",
    # причина: докстринги обязательны только для публичных API (ревью)
    "D100", "D104",
]

[lint.mccabe]
max-complexity = 10

[lint.flake8-tidy-imports]
ban-relative-imports = "all"
""")

w("python/mypy.ini", """# Профиль стандарта v1.2: строгая типизация (Q-03).
[mypy]
python_version = 3.11
strict = True
warn_unreachable = True
disallow_any_generics = True
""")

w("typescript/tsconfig.strict.json", """{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
""")

w("typescript/eslint.config.json", """{
  "rules": {
    "no-explicit-any": "error",
    "no-floating-promises": "error",
    "no-misused-promises": "error",
    "strict-boolean-expressions": "error"
  }
}
""")

w("go/golangci-lint.yml", """# Профиль стандарта v1.2: строгий набор для Go.
linters:
  enable:
    - vet
    - errcheck        # D3: ошибки не глотаются
    - staticcheck
    - gocyclo
    - funlen
    - gosec           # G-домен

linters-settings:
  gocyclo:
    min-complexity: 10
  funlen:
    lines: 60
""")

w("rust/clippy-lints.toml", """# Профиль стандарта v1.2: clippy pedantic минус спорные (причины — комментарии PR).
[lints.clippy]
all = { level = "deny", priority = -1 }
pedantic = { level = "warn", priority = -1 }
# спорные pedantic-правила отключаются точечно с причиной
""")

w("c-cpp/.clang-tidy", """# Профиль стандарта v1.2: core + bugprone + concurrency.
Checks: >
  clang-diagnostic-*,
  clang-analyzer-*,
  cppcoreguidelines-*,
  bugprone-*,
  concurrency-*,
  misc-*,
  -misc-non-private-member-variables-in-classes
WarningsAsErrors: 'clang-diagnostic-*,clang-analyzer-*'
""")

w("java/detekt.yml", """# Профиль стандарта v1.2: строгий detekt (+ ErrorProne в сборке).
build:
  maxIssues: 0
complexity:
  LongMethod:
    active: true
    threshold: 60
  CyclomaticComplexMethod:
    active: true
    threshold: 10
exceptions:
  TooGenericExceptionCaught:
    active: true
""")

w("README.md", """# profiles — строгие конфигурации по стекам (Q-01/Q-02/Q-03)

Готовые конфиги «максимальная строгость» для свежих проектов (`GUIDELINE_profiles_and_dictionaries` §3).
Спорные отключения — с комментарием-причиной прямо в конфиге (конфиги проходят
через собственный Q-11). Ослабление профиля «потому что проект старый» запрещено:
для этого существует храповик целевого репозитория.

| Стек | Файлы |
|---|---|
| Python | `python/ruff.toml`, `python/mypy.ini` |
| TypeScript | `typescript/tsconfig.strict.json`, `typescript/eslint.config.json` |
| Go | `go/golangci-lint.yml` |
| Rust | `rust/clippy-lints.toml` |
| C/C++ | `c-cpp/.clang-tidy` |
| Java/Kotlin | `java/detekt.yml` |

Тест: каждый конфиг разбирается своим форматом и содержит строгие маркеры
(`tests/test_profiles.py`). Полная проверка «собирается на свежем проекте
стека» — при подключении реальных стеков (ограничение отмечено в тесте).
""")
print("profiles: 8 конфигов + README")
