# tooling — gate-runner (companion слоя принуждения)

**Статус:** runner-v0.9 — гейты M1–M4 и L0 реализованы, матрица Б-1…Б-24 закрыта · **Стек:** Python 3.11+, минимум зависимостей (PyYAML, requests)
**Решение владельца 2026-11-17:** companion развивается в этом же репозитории (monorepo); теги `runner-vN`; извлечение в отдельный репозиторий — при появлении внешних потребителей.

## Назначение

Детерминированные guard-гейты стандарта v1.2 для CI целевых репозиториев.
Гейты работают **только** с независимыми источниками (git-диф, реестры
`EXCEPTIONS.md`/baseline/`REPO_CLASS`/CODEOWNERS, API трекера/CI) — описание PR
никогда не является источником фактов (`GUIDELINE_development` §2).

## Матрица гейтов

| Гейт | Назначение | Этап | Статус |
|---|---|---|---|
| `demo_dummy` (DEMO-01) | каркас: полный цикл CI→метка→аннотация | M1 | ✅ |
| Q-11 подавления и конфигурации | храповик, EX-ID, config-fingerprint, `gates-change` | M2 | ✅ Б-1…Б-3, Б-5…Б-8, Б-10 |
| Q-19 аудит исключений и классов | якоря↔реестр, просрочки, ≥3→E-D, доля К3 | M2 | ✅ Б-17…Б-20 |
| L0-детектор периметра | защита ветки, CODEOWNERS, запрет агент-аппрува; fail-closed | C-4 | ✅ (ночной, нужен админ-токен) |
| Q-10 api-diff | обёртка инструментов, метки api-change/breaking, UNAVAILABLE | M4 | ✅ Б-21 |
| Q-17 тайм-ауты (Semgrep) | 8 правил Python, fixtures, Б-22 | M4 | ✅ |
| Q-18 рекурсия/потоки (Semgrep) | 4 правила Python, fixtures, Б-23 | M4 | ✅ |
| Профили 6 стеков | строгие конфиги (гайдлайн §3) | M4 | ✅ |
| Словари 6 экосистем | 24 паттерна, тест-контракт каждого | M4 | ✅ |
| Приёмка C-7 | покрытие 85% (порог 80%), детерминизм всех гейтов (Б-24) | — | ✅ |
| Q-12 эталоны и правила | rule-change/test-change, оракул+код, пересечение меток | M3 | ✅ Б-9, Б-11, Б-12 |
| Q-15 верификация и статус CI | успех при красном CI, чужие прогоны, команды | M3 | ✅ Б-15, Б-16 |
| Q-16 границы задачи | файлы из трекера, вне списка → FAIL, >600 строк | M3 | ✅ Б-13, Б-14 |
| L0-детектор | branch protection, CODEOWNERS, запрет агент-аппрува | — | 🔜 C-4 |
| Q-12 / Q-15 / Q-16 | эталоны, верификация, границы задачи | M3 | 🔜 C-3 |
| Q-10 / Q-17 / Q-18 | api-diff, Semgrep-пакеты | M4 | 🔜 C-5/C-6 |

## Контракт

```
run(GateInputs, GateConfig) -> GateResult
GateInputs = {diff: ParsedDiff, files: RepoFiles, registries: Registries, api: Adapter}
```

- Исходы: `OK | FAIL | SKIP | UNAVAILABLE` (SKIP — только неприменимость, с reason; UNAVAILABLE в PR = красный).
- Exit-коды: `0` OK/SKIP · `1` FAIL · `2` конфигурационная ошибка · `3` UNAVAILABLE.
- Отчёт: JSON `schema:1` (байт-стабильный, без меток времени) — `core/report.py`.
- Метки ставит runner после полного прогона, одним пакетом — не гейт.
- Безопасность: код целевого репо не исполняется; path-escape закрыт; >5 МБ — пропуск.

## Запуск

```
python -m runner.cli run --gate demo_dummy --diff patch.patch --pr 7 --adapter fake
python -m runner.cli gates
```

Метрики эксплуатации (D-1/D-2): CI пишет в одну папку артефакты
`*.report.json` (отчёт schema:1) и `*.meta.json` (`{"author": "...", "pr": 7}`,
создаётся флагами `--author`/`--pr`), затем сборщик строит дашборд
(JSON + Markdown, только агрегаты):

```
python -m runner.cli run --gate q11_suppressions --diff d.patch \
  --author alice --pr 7 --out runs/q11.report.json
python -m runner.cli report collect --reports-dir runs --out-dir dashboard \
  --exceptions EXCEPTIONS.md --baseline baseline/suppressions.yaml
python -m runner.cli baseline migrate --baseline baseline/suppressions.yaml \
  --diff renames.patch --repo-root . --dictionary tooling/dictionaries/python.yaml
```

Тесты (контракт-first; fixtures — мини-дифы + expected.json):

```
pip install -r tooling/requirements.txt -r tooling/requirements-dev.txt
python -m pytest tooling/tests -q \
  --cov=tooling/core --cov=tooling/gates --cov=tooling/runner --cov=tooling/adapters --cov=tooling/collector \
  --cov-report=term --cov-fail-under=80
python -m ruff check tooling
python -m mypy --strict tooling/core tooling/gates tooling/runner tooling/adapters tooling/collector.py
```

## Документирование гейта

Каждый гейт получает `gates/<id>/README.md`: назначение и ссылка на критерий
`QUALITY_GATES.md`; входы/источники; конфиг с дефолтами; список кодов findings;
известные ограничения; как ослабить — никак, кроме E-D (`EXCEPTIONS_POLICY.md`).
