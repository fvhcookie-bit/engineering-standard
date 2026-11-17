# Q-15 «Верификация и статус CI»

**Критерий:** `QUALITY_GATES.md` Q-15 · **TASK:** §3.4 · **Сценарии:** Б-15, Б-16

## Назначение
Источник правды о «зелёном» — только конвейер. Текст PR — объект проверки:
- заявление успеха при красном конвейере → FAIL (механически, Б-15);
- ссылка на прогон, не относящийся к коммиту → FAIL (Б-16);
- упомянутая команда верификации отсутствует в конфигурации репозитория → FAIL;
- не заполнено «стоп-события сессии» → warning (процессное).

## Входы
`pr_text` (объект проверки), `commit_sha`, Adapter: `get_commit_check_status`,
`run_belongs_to_commit`. Fail-closed: API недоступен → UNAVAILABLE.

## Конфиг
`success_markers` (словарь маркеров успеха), `known_commands` (команды
верификации из скриптов/конфигов репо), `stop_events_marker` («стоп-события»),
`pr`.

## Коды findings
`SUCCESS_MARKER_AT_RED` · `UNKNOWN_RUN_REFERENCE` · `UNKNOWN_VERIFY_COMMAND` ·
`STOP_EVENTS_MISSING` (warning).
