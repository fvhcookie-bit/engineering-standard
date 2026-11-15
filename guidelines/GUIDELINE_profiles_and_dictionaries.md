# ГАЙДЛАЙН: профили конфигураций, словари подавлений, правила Q-17/Q-18

**Версия:** 1.0 · Для кого: сопроводащий companion-репозитория; тот, кто добавляет новый язык/экосистему.

---

## 1. Словарь подавлений (Q-11)

### 1.1. Формат

`dictionaries/<ecosystem>.yaml`, схема версионируется:

```yaml
schema: 1
ecosystem: python
patterns:
  - id: noqa                 # стабильный id вида подавления
    regex: '#\s*noqa(?::\s*(?P<codes>[A-Z0-9,]+))?'
    languages: [python]
  - id: type_ignore
    regex: '#\s*type:\s*ignore'
    languages: [python]
  - id: pytest_skip
    regex: '@pytest\.mark\.(skip|skipif|xfail)'
    languages: [python]
```

Обязательные категории (минимум, из `QUALITY_GATES.md` Q-11): `noqa`/`flake8`, `nolint`, `# type: ignore` + `pyright: ignore`, `@ts-ignore`/`@ts-expect-error`/`@ts-nocheck`, `noinspection`, `#[allow]` (включая `#![allow]` crate-level), `@SuppressWarnings`, `eslint-disable` (+ per-line/per-file формы), `as any`, `unsafe` (Rust), `pytest.mark.skip|xfail|skipif`, `@Ignore`/`@Disabled` (JUnit), `ignore_errors` (mypy per-module), per-file-ignores и exclude-пути инструментов (отдельная категория `path_excludes`).

### 1.2. Правила сопровождения

1. **Id паттерна стабильны** — на них ссылается baseline; переименование id = миграция baseline (инструментом `gate-runner baseline migrate`), а не правка руками.
2. **Тест-контракт словаря:** для каждого `id` — fixture-файл с положительным и отрицательным примером; словарь без fixture не проходит CI companion-репо.
3. **Новый паттерн = PR с changelog-записью** («добавлен механизм X, найден в …»); молчаливое расширение запрещено — иначе сам словарь становится каналом ослабления.
4. Комментарий-причина и `EX-…`-ID ищутся на **той же строке или строке выше** подавления (конфигурируется per-id: `reason_proximity: same_line | line_above`).

### 1.3. Baseline-файл целевого репозитория

```yaml
# baseline/suppressions.yaml
schema: 1
counts:                      # вид подавления → glob → максимум допустимого
  python/noqa:      { "src/**": 12, "tests/**": 40 }
  python/type_ignore:{ "src/legacy/**": 5 }
fingerprint:                 # последняя зафиксированная эффективная конфигурация
  eslint: { "eslint.config.mjs": "sha256:…" }
generated_at: 2026-11-14T00:00:00Z
generated_by: gate-runner 1.x
```

Правила: рост любого счётчика → FAIL; снижение допустимо (PR может его внести); файл под CODEOWNERS владельца стандарта; изменение baseline и кода — разные PR (`baseline-reset`).

## 2. Config-fingerprint (детекция «смягчения» конфигов)

Для каждого поддерживаемого линтера — модуль-парсер, возвращающий **канонический JSON эффективных правил**: включённые правила, уровни, пороги, ignore-пути. Fingerprint = SHA-256 канонического JSON. Baseline хранит последние fingerprint'ы; любое расхождение или новый конфиг-файл инструмента в дереве → `gates-change`.

Минимальный набор парсеров на старте: ESLint (flat + legacy JSON), ruff/flake8 (pyproject/setup.cfg), golangci-lint, mypy (вкл. per-module overrides), tsc (tsconfig), clippy (Cargo.toml `[lints]` + clippy.toml), clang-tidy (.clang-tidy). Для конфигов-скриптов (`.eslintrc.js`) — парсим JSON-подобные формы, ограничение помечается в README парсера.

## 3. Строгие профили (Q-01/Q-02/Q-03)

`profiles/<lang>/` — готовые конфиги «максимальная строгость» для свежего проекта:

| Язык | Состав профиля |
|---|---|
| Python | `ruff.toml` (весь набор + `select: ALL` минус спорные, задокументированные), `mypy.ini` strict, semgrep-набор bandit-класса |
| TypeScript | `tsconfig` strict (+ noUncheckedIndexedAccess), `eslint.config` strict-typescript, запрет `any` без suppress-пути |
| Go | `golangci-lint.yml`: vet, errcheck, staticcheck, gocyclo/funlen в warning-режиме |
| Rust | `Cargo.toml [lints]` clippy pedantic-минус-спорные, `#![deny(warnings)]` для lib-крейтов |
| C/C++ | `.clang-tidy` (core, bugprone, concurrency), флаги `-Wall -Wextra -Wpedantic -Werror`, sanitizer-конфиги для тестов |
| Java/Kotlin | ErrorProne + detekt/ktlint strict-конфиг |

Правила сопровождения: у каждого профиля владелец; тест «профиль применяется к свежесозданному проекту стека и собирается без ошибок»; спорные отключения — с комментарием-причиной прямо в конфиге (сами конфиги проходят через гейт Q-11 companion-репо).

## 4. Правила Semgrep для Q-17/Q-18

### 4.1. Структура

`semgrep/q17-timeouts/<lang>/*.yaml` — каждое правило: id (`q17-http-no-timeout`), severity по классу проекта (задаётся переменной профиля), message со ссылкой на принцип (B6), fix-подсказка.

### 4.2. Примеры (Python)

```yaml
- id: q17-requests-no-timeout
  message: "B6/Q-17: HTTP-запрос без тайм-аута — внешнее взаимодействие обязано иметь лимит"
  severity: ERROR
  languages: [python]
  patterns:
    - pattern-either:
        - pattern: requests.get($URL, ...)
        - pattern: requests.post($URL, ...)
    - pattern-not: requests.$M($URL, ..., timeout=$T, ...)
```

```yaml
- id: q18-recursion-no-depth
  message: "A2/Q-18: рекурсия по внешним данным без предела глубины"
  severity: ERROR
  languages: [python]
  patterns:
    - pattern: |
        def $F(..., $DEPTH, ...):
            ...
            $F(..., $DEPTH + 1, ...)
```

### 4.3. Требования к пакету правил

1. На каждое правило — **positive и negative fixture** (код, который ловится; код, который не должен ловиться) — CI companion-репо гоняет `semgrep --test`.
2. Правило помечает покрываемый принцип (B6/A2/A3) — для трассировки в отчёте.
3. Запрещены правила с `pattern-regex` «широкого захвата», дающие > 5% ложных срабатываний на fixtures реальных репо (замеряется при добавлении).
4. Минимальный объём на основной язык: Q-17 — 8–12 правил, Q-18 — 4–6.

## 5. api-diff инструменты (Q-10)

| Экосистема | Инструмент | Что сравнивает |
|---|---|---|
| JVM | kotlin-api-diff / japicmp / revapi | jar/модуль против базовой версии |
| Rust | `cargo public-api` + diff | публичная поверхность |
| Go | `go-apidiff` | пакеты/функции |
| Python | `griffe`/`pyapi-advisory`-подходы + own | экспорты модулей (ограничение: нет строгих типов — пометка в отчёте) |
| TS/JS | api-extractor + api-diff | d.ts-поверхность |
| Protobuf/OpenAPI | buf breaking / oasdiff | схемы |

Отсутствие инструмента для языка = `UNAVAILABLE` гейта Q-10 с явной записью (не молчаливый OK).

## 6. Процедура добавления нового языка/экосистемы

1. Открыть задачу в companion-репо с чек-листом: словарь подавлений + fixture'ы; парсер config-fingerprint; профиль линтеров/типов; правила Q-17/Q-18 (если применимо); api-diff инструмент (если применимо); запись в README матрицы стеков.
2. Каждый артефакт — через PR с тестами (словарный контракт, semgrep --test, профиль на свежем проекте).
3. Изменения, ослабляющие проверки (удаление правила, понижение уровня) — метка `gates-change` и владелец стандарта как ревьюер (в companion-репо действует его собственный Q-11).

## 7. Чего делать нельзя

- Добавлять паттерны/правила «на всякий случай», порождающие шум: ложные срабатывания убивают доверие к гейтам быстрее, чем пропуски.
- Править baseline целевого репо руками: только через `gate-runner baseline` (миграция при механических перемещениях) или `baseline-reset` PR.
- Хранить в companion-репо данные целевых репозиториев (код, отчёты с содержимым файлов) — только агрегаты и метрики.
- Ослаблять профиль «потому что проект старый»: для этого существует храповик целевого репозитория, а не понижение профиля.
