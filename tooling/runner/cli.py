"""gate-runner CLI (M1): запуск гейта на дифе, отчёт JSON, коды выхода 0/1/2/3.

  python -m runner.cli run --gate demo_dummy --diff patch.patch [--repo-root DIR] [--pr N]
  python -m runner.cli gates
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from adapters.fake import FakeAdapter
from core.diff import parse_unified_diff
from core.files import RepoFiles
from core.gate_api import GateInputs
from core.report import build_report, render_report, validate_report
from gates import GATES, get_gate

EXIT_CODES = {"OK": 0, "SKIP": 0, "FAIL": 1, "UNAVAILABLE": 3}


def _build_adapter(name: str, pr: int) -> Any:
    if name == "fake":
        return FakeAdapter()
    if name == "github":
        from adapters.github import GitHubAdapter

        return GitHubAdapter(repo="OWNER/REPO")
    if name == "gitlab":
        from adapters.gitlab import GitLabAdapter

        return GitLabAdapter(project_id="PROJECT")
    raise ValueError(f"неизвестный адаптер: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gate-runner", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="прогнать гейт на дифе")
    p_run.add_argument("--gate", required=True, help="короткое имя гейта (см. `gates`)")
    p_run.add_argument("--diff", required=True, help="путь к файлу unified diff (git diff -M -C)")
    p_run.add_argument("--repo-root", default="", help="корень целевого репозитория (для чтения файлов)")
    p_run.add_argument("--pr", type=int, default=0, help="номер PR (для адаптера)")
    p_run.add_argument("--adapter", choices=["fake", "github", "gitlab"], default="fake")
    p_run.add_argument("--out", default="", help="записать отчёт в файл (иначе stdout)")

    sub.add_parser("gates", help="список зарегистрированных гейтов")

    args = parser.parse_args(argv)

    if args.command == "gates":
        for name in sorted(GATES):
            gate = get_gate(name)
            print(f"{name}: {gate.id} v{gate.version}")
        return 0

    try:
        gate = get_gate(args.gate)
    except KeyError as exc:
        print(f"ошибка конфигурации: {exc}", file=sys.stderr)
        return 2

    diff_path = Path(args.diff)
    if not diff_path.is_file():
        print(f"ошибка конфигурации: диф не найден: {args.diff}", file=sys.stderr)
        return 2

    from core.registries import Registries

    inputs = GateInputs(
        diff=parse_unified_diff(diff_path.read_text(encoding="utf-8", errors="replace")),
        files=RepoFiles(root=Path(args.repo_root) if args.repo_root else None),
        registries=Registries.empty(),
        api=_build_adapter(args.adapter, args.pr),
    )

    result = gate.run(inputs, config={})
    report = build_report(result)
    errors = validate_report(report)
    if errors:
        print(f"внутренняя ошибка: отчёт не прошёл валидацию: {errors}", file=sys.stderr)
        return 2

    text = render_report(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)

    if args.pr and result.labels:
        inputs.api.set_labels(args.pr, result.labels)
        inputs.api.post_summary(
            args.pr,
            f"**{result.gate_id}**: {result.status.value}; findings: {len(result.findings)}",
        )
    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    sys.exit(main())
