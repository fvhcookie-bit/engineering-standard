# Q-11 «Подавления и конфигурации гейтов» (guard-гейт)

**Критерий:** `QUALITY_GATES.md` Q-11 · **TASK:** §3.1 · **Сценарии:** Б-1…Б-3, Б-5…Б-8, Б-10

## Назначение
Храповик подавлений: рост любого счётчика по (вид, glob) — FAIL, компенсации
запрещены; каждое новое подавление — с валидным `EX-…` из `EXCEPTIONS.md`;
изменение эффективной конфигурации инструментов — принудительная `gates-change`.

## Входы (независимые источники)
- git-диф (`-M -C`), только добавленные строки;
- `baseline/suppressions.yaml` (counts + fingerprint) — через `Registries`;
- `EXCEPTIONS.md` — через `Registries`;
- словарь подавлений (config `patterns`), globs конфигов (config `config_files`).

## Конфиг (ключи / дефолты)
| Ключ | Дефолт |
|---|---|
| `patterns` | — (обязателен; загружается runner'ом из словаря) |
| `language_ext` | `{"python": [".py"]}` |
| `config_files` | `[]` — globs конфиг-файлов инструментов и CI |
| `baseline_paths` | `["baseline/**", "dictionaries/**"]` |
| `second_reviewer_threshold` | `3` |

## Коды findings
`SUPPRESS_NO_EXID` · `SUPPRESS_UNKNOWN_EXID` · `SUPPRESS_EXID_EXPIRED` ·
`BASELINE_GROWTH` · `BASELINE_WITH_CODE` · `CONFIG_FILE_TOUCHED` (info) ·
`CONFIG_FINGERPRINT_CHANGED` (warning).

## Семантика E-A vs E-C
Подавление с валидным EX-ID (E-C) — легитимно в PR и **не** считается в храповике
(наблюдается Q-19); без EX-ID (E-A) — считается против baseline.

## Ограничения
- ESLint: парсятся JSON-формы (`.eslintrc.json`, `eslint.config.json`); `.mjs`-конфиги —
  fingerprint недоступен (ограничение парсера, помечено при конфигурации).
- Миграция baseline — только `gate-runner baseline migrate` (Б-10), руками — никогда.
- Ослабление гейта — никак, кроме E-D (`EXCEPTIONS_POLICY.md`).
