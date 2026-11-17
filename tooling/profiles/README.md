# profiles — строгие конфигурации по стекам (Q-01/Q-02/Q-03)

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
