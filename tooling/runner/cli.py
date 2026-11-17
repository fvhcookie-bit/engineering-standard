"""gate-runner CLI (M1/M2): запуск гейтов, отчёт JSON, коды выхода 0/1/2/3.

  python -m runner.cli run --gate demo_dummy --diff patch.patch [--pr N] [--config cfg.json]
  python -m runner.cli run --gate q19_audit --repo-root DIR [--config cfg.json]
  python -m runner.cli baseline migrate --baseline PATH --diff PATH --repo-root DIR
  python -m runner.cli gates
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from adapters.fake import FakeAdapter
from core.diff import parse_unified_diff
from core.files import RepoFiles
from core.gate_api import GateInputs
from core.registries import Registries
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


def _load_config(path: str) -> dict[str, Any]:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError("конфиг не объект")
    if "dictionary" in cfg:
        from core.dictionary import load_dictionary

        cfg["patterns"] = load_dictionary(
            Path(cfg["dictionary"]).read_text(encoding="utf-8"))
    return cfg


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        gate = get_gate(args.gate)
    except KeyError as exc:
        print(f"ошибка конфигурации: {exc}", file=sys.stderr)
        return 2

    if args.diff:
        diff_path = Path(args.diff)
        if not diff_path.is_file():
            print(f"ошибка конфигурации: диф не найден: {args.diff}", file=sys.stderr)
            return 2
        diff = parse_unified_diff(diff_path.read_text(encoding="utf-8", errors="replace"))
    else:
        diff = []

    root = Path(args.repo_root) if args.repo_root else None
    if root is None and args.gate in ("q19_audit",):
        print("ошибка конфигурации: q19_audit требует --repo-root", file=sys.stderr)
        return 2

    try:
        config = _load_config(args.config) if args.config else {}
    except (OSError, ValueError, KeyError) as exc:
        print(f"ошибка конфигурации: {exc}", file=sys.stderr)
        return 2

    inputs = GateInputs(
        diff=diff,
        files=RepoFiles(root=root),
        registries=Registries.from_repo(root) if root else Registries.empty(),
        api=_build_adapter(args.adapter, args.pr),
    )

    result = gate.run(inputs, config=config)
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


def _cmd_baseline(args: argparse.Namespace) -> int:
    from core.baseline import migrate

    baseline_path = Path(args.baseline)
    repo_root = Path(args.repo_root)
    if not baseline_path.is_file() or not repo_root.is_dir() or not Path(args.diff).is_file():
        print("ошибка конфигурации: проверьте --baseline/--diff/--repo-root", file=sys.stderr)
        return 2
    from core.dictionary import load_dictionary as _ld
    patterns = _ld(Path(args.dictionary).read_text(encoding="utf-8"))
    from core.registries import load_baseline

    baseline = load_baseline(baseline_path.read_text(encoding="utf-8"))
    diff_files = parse_unified_diff(Path(args.diff).read_text(encoding="utf-8", errors="replace"))
    new_baseline = migrate(baseline, RepoFiles(root=repo_root), patterns, {}, diff_files)
    import yaml

    baseline_path.write_text(
        "# baseline подавлений (храповик Q-11)\n"
        + yaml.safe_dump(new_baseline, allow_unicode=True, sort_keys=True),
        encoding="utf-8", newline="\n")
    print(f"baseline мигрирован: {baseline_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gate-runner", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="прогнать гейт")
    p_run.add_argument("--gate", required=True, help="короткое имя гейта (см. `gates`)")
    p_run.add_argument("--diff", default="", help="файл unified diff (git diff -M -C); не нужен деревьевым гейтам")
    p_run.add_argument("--repo-root", default="", help="корень целевого репозитория")
    p_run.add_argument("--config", default="", help="JSON-конфиг гейта (словарь, globs, лимиты)")
    p_run.add_argument("--pr", type=int, default=0, help="номер PR (для адаптера)")
    p_run.add_argument("--adapter", choices=["fake", "github", "gitlab"], default="fake")
    p_run.add_argument("--out", default="", help="записать отчёт в файл (иначе stdout)")

    p_base = sub.add_parser("baseline", help="работа с baseline храповика")
    p_base_sub = p_base.add_subparsers(dest="baseline_cmd", required=True)
    p_mig = p_base_sub.add_parser("migrate", help="пересчёт baseline по head (механический PR, Б-10)")
    p_mig.add_argument("--baseline", required=True)
    p_mig.add_argument("--diff", required=True, help="диф механического PR (rename-карта)")
    p_mig.add_argument("--repo-root", required=True, help="дерево head")
    p_mig.add_argument("--dictionary", required=True, help="словарь подавлений")

    sub.add_parser("gates", help="список зарегистрированных гейтов")

    args = parser.parse_args(argv)

    if args.command == "gates":
        for name in sorted(GATES):
            gate = get_gate(name)
            print(f"{name}: {gate.id} v{gate.version}")
        return 0
    if args.command == "baseline":
        return _cmd_baseline(args)
    return _cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
