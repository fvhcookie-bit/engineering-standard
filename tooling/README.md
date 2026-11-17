# tooling — gate-runner (companion слоя принуждения)

**Статус:** C-1 (каркас, M1) — в работе · **Стек:** Python 3.11+, минимум зависимостей (PyYAML, requests)
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
| Q-11 подавления и конфигурации | храповик, EX-ID, config-fingerprint, `gates-change` | M2 | 🔜 C-2 |
| Q-19 аудит исключений и классов | якоря↔реестр, просрочки, ≥3→E-D, доля К3 | M2 | 🔜 C-2 |
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

Тесты (контракт-first; fixtures — мини-дифы + expected.json):

```
pip install -r tooling/requirements.txt -r tooling/requirements-dev.txt
python -m pytest tooling/tests -q
python -m ruff check tooling
python -m mypy --strict tooling/core tooling/gates tooling/runner tooling/adapters
```

## Документирование гейта

Каждый гейт получает `gates/<id>/README.md`: назначение и ссылка на критерий
`QUALITY_GATES.md`; входы/источники; конфиг с дефолтами; список кодов findings;
известные ограничения; как ослабить — никак, кроме E-D (`EXCEPTIONS_POLICY.md`).
