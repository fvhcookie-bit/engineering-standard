# DEMO-01 (демонстрационный гейт каркаса, M1)

Полный цикл CI→отчёт→метка на тривиальном правиле: добавленная строка с маркером
`FORBIDDEN-DEMO` → error `DEMO_FORBIDDEN_MARKER` + метка `demo-label`.

Fixture: `fixtures/demo_dummy/` (diff.patch + expected.json, байт-сравнение).
Используется приёмкой M1 и как образец структуры гейта для новых реализаций.
