"""Адаптеры CI/хостинга: выставление меток, аннотации, чтение ревью.

Протокол — adapters.base.Adapter; реализации: github.py, gitlab.py (тонкие
клиенты), fake.py (offline-регистратор для тестов). Токены — только из
окружения CI (GUIDELINE_development §6.4).
"""
