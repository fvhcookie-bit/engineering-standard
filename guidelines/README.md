# Гайдлайны: реализация guard-гейтов стандарта v1.1

Эта папка содержит задание и гайдлайны для разработки companion-репозитория (реализации автоматических проверок стандарта `../standards/`).

| Документ | Содержание |
|---|---|
| [TASK_guard-gates.md](TASK_guard-gates.md) | Техническое задание: объём, требования по каждому гейту, приёмочные сценарии, этапы и оценки |
| [GUIDELINE_development.md](GUIDELINE_development.md) | Архитектура и правила разработки: каркас runner, контракт гейта, анти-самоотчётность, fail-режимы, тестирование, интеграция CI |
| [GUIDELINE_profiles_and_dictionaries.md](GUIDELINE_profiles_and_dictionaries.md) | Словари подавлений, config-fingerprint, строгие профили линтеров по языкам, правила Semgrep для Q-17/Q-18 |

**Нормативная база:** `../standards/ENGINEERING_PRINCIPLES.md` (v1.1), `../standards/QUALITY_GATES.md` (v1.1, каталог Q-01…Q-19), `../standards/EXCEPTIONS_POLICY.md` (v1.1). При расхождении — нормативны стандарты, не гайдлайны.

**Ключевой инвариант всех проверок:** гейт никогда не берёт данные из описания PR или иных деклараций автора — только из git, реестров репозитория (`EXCEPTIONS.md`, baseline, `REPO_CLASS`) и API (трекер, CI).
