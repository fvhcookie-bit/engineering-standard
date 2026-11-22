# tooling — gate-runner (the enforcement layer's companion)

**Status:** runner-v1.0 — M1–M4 gates and L0, the Б-1…Б-24 matrix, operations metrics (track D) · **Stack:** Python 3.11+, minimal dependencies (PyYAML, requests)
**Official translation.** The authoritative text is the Russian original (`tooling/README.md`); in case of divergence the Russian wording prevails.
**Owner decision 2026-11-17:** the companion is developed in this same repository (monorepo); `runner-vN` tags; extraction into a separate repository — when external consumers appear.

## Purpose

Deterministic guard gates of standard v1.2 for the CI of target repositories.
The gates work **only** with independent sources (the git diff, the
`EXCEPTIONS.md`/baseline/`REPO_CLASS`/CODEOWNERS registries, the tracker/CI API) —
the PR description is never a source of facts (`GUIDELINE_development` §2).

## The gate matrix

| Gate | Purpose | Stage | Status |
|---|---|---|---|
| `demo_dummy` (DEMO-01) | skeleton: the full CI→label→annotation cycle | M1 | ✅ |
| Q-11 suppressions and configurations | ratchet, EX-ID, config fingerprint, `gates-change` | M2 | ✅ Б-1…Б-10 |
| Q-19 exceptions and classes audit | anchors↔registry, expiries, ≥3→E-D, the К3 share | M2 | ✅ Б-17…Б-20 |
| L0 perimeter detector | branch protection, CODEOWNERS, the agent-approval ban; fail-closed | C-4 | ✅ (nightly, needs an admin token) |
| Q-10 api-diff | tool wrappers, api-change/breaking labels, UNAVAILABLE | M4 | ✅ Б-21 |
| Q-17 timeouts (Semgrep) | 8 Python rules, fixtures, Б-22 | M4 | ✅ |
| Q-18 recursion/loops (Semgrep) | 4 Python rules, fixtures, Б-23 | M4 | ✅ |
| Profiles of 6 stacks | strict configs (GUIDELINE_profiles_and_dictionaries.md §3) | M4 | ✅ |
| Dictionaries of 7 ecosystems | 25 patterns, a test contract per pattern | M4 | ✅ |
| C-7 acceptance | coverage 85% (threshold 80%), determinism of all gates (Б-24) | — | ✅ |
| Q-12 references and rules | rule-change/test-change, oracle+code, label intersection | M3 | ✅ Б-9, Б-11, Б-12 |
| Q-15 verification and CI status | success claims on red CI, foreign runs, commands | M3 | ✅ Б-15, Б-16 |
| Q-16 task boundaries | files from the tracker, outside the list → FAIL, >600 lines | M3 | ✅ Б-13, Б-14 |

## The contract

```
run(GateInputs, GateConfig) -> GateResult
GateInputs = {diff: ParsedDiff, files: RepoFiles, registries: Registries, api: Adapter}
```

- Outcomes: `OK | FAIL | SKIP | UNAVAILABLE` (SKIP — inapplicability only, with a reason; UNAVAILABLE in a PR = red).
- Exit codes: `0` OK/SKIP · `1` FAIL · `2` configuration error · `3` UNAVAILABLE.
- The report: JSON `schema:1` (byte-stable, no timestamps) — `core/report.py`.
- Labels are set by the runner after a full run, in one batch — not by a gate.
- Security: the target repository's code is not executed; path escape is closed; >5 MB — skipped.

## Running

```
python -m runner.cli run --gate demo_dummy --diff patch.patch --pr 7 --adapter fake
python -m runner.cli gates
```

The `github`/`gitlab` adapters take the target from the CI environment (`GITHUB_REPOSITORY`, `CI_PROJECT_ID`, `CI_API_V4_URL`) or from the `--repo` / `--project-id` arguments; if neither is set — a configuration error (code 2).

Operations metrics (D-1/D-2): CI writes `*.report.json` (a schema:1 report) and
`*.meta.json` (`{"author": "...", "pr": 7}`, created by the `--author`/`--pr` flags)
into one artifacts folder; the collector then builds a dashboard
(JSON + Markdown, aggregates only):

```
python -m runner.cli run --gate q11_suppressions --diff d.patch \
  --author alice --pr 7 --out runs/q11.report.json
python -m runner.cli report collect --reports-dir runs --out-dir dashboard \
  --exceptions EXCEPTIONS.md --baseline baseline/suppressions.yaml
python -m runner.cli baseline migrate --baseline baseline/suppressions.yaml \
  --diff renames.patch --repo-root . --dictionary tooling/dictionaries/python.yaml
```

Tests (contract-first; fixtures — mini-diffs + expected.json):

```
pip install -r tooling/requirements.txt -r tooling/requirements-dev.txt
python -m pytest tooling/tests -q \
  --cov=tooling/core --cov=tooling/gates --cov=tooling/runner --cov=tooling/adapters --cov=tooling/collector \
  --cov-report=term --cov-fail-under=80
python -m ruff check tooling
python -m mypy --strict tooling/core tooling/gates tooling/runner tooling/adapters tooling/collector.py
```

Coverage: an 80% threshold in CI (in fact ~86%). The uncovered part is deliberate: the
network wrappers of the github/gitlab adapters are not covered by unit tests (the project's
rule: the network — only via FakeAdapter), plus rare parsing error branches.

- The self-config (`self_q11.json`): `baseline_paths` — `tooling/baseline/**` only;
  touching the dictionaries produces a `gates-change` label (not blocking). Decision 2026-11-18:
  the companion's dictionaries are detection config, changed together with their generators
  (`tools/generators/`); the ratchet compensation (Б-7) does not apply to them; the strict
  baseline+code separation is kept for real baseline files.

## Documenting a gate

Every gate gets `gates/<id>/README.md`: the purpose and a link to the
`QUALITY_GATES.md` criterion; inputs/sources; the config with defaults; the list of finding codes;
known limitations; how to weaken — in no way, except E-D (`EXCEPTIONS_POLICY.md`).
