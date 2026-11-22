# GUIDELINE: developing guard gates

**Version:** 1.0 · Audience: the developer/agent implementing the checks from `TASK_guard-gates.md`.
**Official translation.** The authoritative text is the Russian original (`guidelines/GUIDELINE_development.md`); in case of divergence the Russian wording prevails. Gate IDs, finding codes, labels, and file paths are not translated.

---

## 1. Architecture

```
companion — the tooling/ directory (monorepo)
├── runner/            # CLI: gate-runner (entry point, aggregation)
├── gates/             # gates: q11_suppressions/, q12_protected/, q15_verify/,
│                      #         q16_scope/, q19_audit/, q10_api_diff/
├── core/              # git-diff parser, Findings, JSON report, registries, schemas
├── adapters/          # github/, gitlab/, trackers/ (jira, gitlab-issues)
├── dictionaries/      # suppression dictionaries per ecosystem (see the profiles guideline)
├── profiles/          # strict linter/type configs per language
├── semgrep/           # Q-17/Q-18 rule packages
├── fixtures/          # scenario mini-repositories (the Б-1…Б-24 matrix)
└── tests/             # gate contract tests + dictionary test contracts
```

**The purity principle:** every gate is a pure function over explicit inputs:

```
run(inputs: GateInputs, config: GateConfig) -> GateResult
GateInputs = {diff: ParsedDiff, files: RepoFiles, registries: Registries, api: Adapters}
```

No hidden environment reads inside a gate: everything goes through `GateInputs` — this makes testability trivial and turns the self-reporting ban into a structural property, not a disciplinary one.

## 2. The source-independence rule (the main one)

1. A gate receives data **only** from: git (diff, tree), the repository's registry files (`EXCEPTIONS.md`, baseline, `REPO_CLASS`, CODEOWNERS), the tracker/CI API.
2. The PR description, the author's comments, the title — **only as objects of inspection** (Q-15 looks for markers in them), never as a source of facts.
3. Labels (`gates-change`, `rule-change`, `api-change`, `breaking`, `test-change`, `perf`, `baseline-reset`) are set by **a bot from diff-analysis results**; a request in the PR text does not create a label.
4. If the data is insufficient for a conclusion — status `SKIP`/`UNAVAILABLE` with a reason. A silent OK on incomplete data is prohibited.

## 3. The gate contract

Every gate implements the interface:

```python
class Gate:
    id: str                      # "Q-11"
    def run(self, inputs: GateInputs, config: GateConfig) -> GateResult
```

`GateResult` → `Findings[]` + `status` + `labels` + `stats` (the report schema — in the TASK §4.6). Rules:

- **Finding codes** — stable string constants (`SUPPRESS_NO_EXID`, `BASELINE_GROWTH`, `SCOPE_OUTSIDE_TASK`…), documented in the gate's README; consumers (CI annotations, dashboards) rely on codes, not on message texts.
- **Severity:** `error` (FAIL), `warning`, `info` — displayed in the annotations accordingly.
- **FAIL aggregation:** any `error` → status FAIL; warnings do not affect the exit code.
- **Process exit codes:** `0` OK/acceptable-SKIP, `1` FAIL, `2` configuration error, `3` UNAVAILABLE. The CI job maps: FAIL/3 → red, SKIP → green with a note in the report.

## 4. Working with the diff

- The diff parser (core) returns structured changes: files, hunks, added/removed lines; **rename/copy detection enabled** (git `-M -C`) — renames are not counted as "new code" (scenario Б-10).
- Suppressions and calls are extracted **only from added lines**; removed ones are ignored.
- For parsing linter configs — not a regex over text but structural parsing (JSON/YAML/TOML parsers; for `.eslintrc.js` — limited: JSON-shaped variants + an explicitly noted limitation in the gate's README).

## 5. Fail / Skip / Unavailable

| Outcome | When | In the report |
|---|---|---|
| `OK` | checked, no violations | — |
| `FAIL` | there are error-findings | findings |
| `SKIP` | the gate does not apply (no task file list; no budget — no Q-13) | `reason` is mandatory |
| `UNAVAILABLE` | infrastructure unavailable (tracker/CI API, timeout) | `reason` + a retry policy |

- `SKIP` never arises from an error — only from per-config inapplicability.
- `UNAVAILABLE` in a PR gate → the job is red (fail-closed), except cases explicitly allowed by the repository's policy (`QUALITY_GATES.md` §6, "the policy for unavailable CI").

## 6. Security

1. **Repository code is not executed.** We parse texts, we do not run them; hooks/scripts of the target repository are never invoked by the runner.
2. **Anti-injection:** repository content is data. Strings from code/configs/PRs are not passed to a shell, are not interpreted as paths/commands; when logging — escaping.
3. **Paths:** normalization, no escaping the repository root (symlink escape), a limit on the processed file size (e.g., > 5 MB — skip with info).
4. **Tokens:** minimal scope (labels: write, pulls: read, issues: write for Q-19); secrets — from the CI environment only; no secrets in companion configs.
5. **Pinning:** target repositories pin the runner version (SHA); updates — via a PR with a changelog entry.

## 7. Testing (contract-first)

1. **Golden fixtures:** every acceptance scenario Б-* (TASK §5) — a mini-repository: `fixtures/<scenario>/base/` and `/head/` (git snapshots) + `expected.json` (the expected findings). The test = a gate run on the fixture + a diff comparison of reports. A changed report — the test fails.
2. **The suppression dictionary's test contract:** a fixture per pattern of every ecosystem (a dictionary without coverage fails); plus a "the dictionary does not grow silently" test (a new pattern requires a changelog entry).
3. **Negative tests of anti-self-reporting:** a separate set — "what if the author writes plausible data into the PR" (Б-1, Б-14, Б-15, Б-16): the gate must ignore them.
4. **Determinism:** the test runs the gate twice and compares the reports byte-for-byte (after runner-path normalization).
5. **Own hygiene:** the companion repository gates itself with Q-11 (its own dictionary), test coverage ≥ 80% on `gates/` and `core/`, strict lint/types.

## 8. CI integration

- **GitHub Actions:** a `guard-gates` job with a per-gate matrix; `permissions: pull-requests: write, contents: read`; a step — running the runner by a pinned SHA; findings → job annotations + PR labels via the API; the JSON report — a PR artifact.
- **GitLab CI:** likewise, `merge_request_event`; labels via a project access token.
- **Do not duplicate sources:** the required checks — these jobs only; do not build policy on "the agent's local runs".
- **Label order:** labels are set after computing all findings in one run (not in parts).

## 9. Observability

- Every run writes a report artifact (JSON) — the source for dashboards (exceptions, suppressions, escalations — `EXCEPTIONS_POLICY.md` §7).
- Per-subject metrics (author/agent: number of PRs, suppressions, guard labels, repeat violations) — from the artifacts, an aggregator as part of the runner (`report collect`), export to an arbitrary storage.
- Logs — structured, without the content of inspected files (paths — yes, content — no: minimizing leaks through logs).

## 10. Documenting a gate

A README per gate (`gates/<id>/README.md`): the purpose and a link to the criterion in `QUALITY_GATES.md`; inputs/sources; the config (all keys with defaults); the list of finding codes; known limitations and false positives; how to disable/weaken — **in no way, except E-D** (a link to `EXCEPTIONS_POLICY.md`).
