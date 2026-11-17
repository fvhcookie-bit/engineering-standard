# generators — генераторы fixtures-артефактов companion

Разовые генераторы этапов C-2…C-6, сохранённые для перегенерации. Правило:
артефакты (`tooling/fixtures`, `tooling/dictionaries`, `tooling/profiles`,
`tooling/semgrep/fixtures`) правятся **в генераторе**, затем перегенерируются —
не руками в самих артефактах (ручные правки затираются следующим запуском).

| Скрипт | Генерирует | Когда запускать |
|---|---|---|
| `_c2_fixtures.py` | `tooling/fixtures/b_01…b_20` (сценарии Б для Q-11/Q-19) + словарные контракты python | изменение матрицы Б для M2 |
| `_c3_fixtures.py` | `tooling/fixtures/b_09, b_11…b_16` (Б для Q-12/Q-15/Q-16) | изменение матрицы Б для M3 |
| `_c5_semgrep_fixtures.py` | `tooling/semgrep/fixtures/**` (позитив/негатив по каждому ID правил; сверяет ID с rules.yaml) | изменение правил Q-17/Q-18 |
| `_c5_profiles.py` | `tooling/profiles/**` (строгие конфиги 6 стеков) | изменение профилей |
| `_c6_dicts.py` | `tooling/dictionaries/*.yaml` + их контракты (6 экосистем; python.yaml ведётся отдельно в `_c2_fixtures.py`) | изменение словарей |

Запуск из корня репозитория: `python tools/generators/<script>.py`.
Контроль: перегенерация без изменений входов даёт нулевой diff (проверено
2026-11-18, блок 6).
