# TASK: implementing the standard's guard gates (the companion repository)

**Version:** 1.0 · **Basis:** `../QUALITY_GATES.md` (the gate catalog; EN — `../../standards/en/QUALITY_GATES.md`), `../../standards/ENGINEERING_PRINCIPLES.md`
**Default implementation stack:** Python 3.11+ (minimal dependencies: PyYAML, requests/urllib3); Go is allowed — by agreement with the standard's owner.
**Official translation.** The authoritative text is the Russian original (`guidelines/TASK_guard-gates.md`); in case of divergence the Russian wording prevails. Gate IDs, scenario IDs (Б-1…Б-24), labels, and file paths are not translated.

---

## 1. The goal and the scope

Create a set of deterministic CI scripts that enforce the standard's guard gates in target repositories. The gates work with **independent data sources** (git, the repository's registries, the tracker/CI API) and never with the PR author's declarations.

**In scope:**

| Package | Gates | Priority |
|---|---|---|
| The runner skeleton + the report contract + the test infrastructure | — | M1, blocker |
| Suppressions and gate configurations | Q-11 | M2, blocker |
| The exceptions and classes audit | Q-19 | M2, blocker |
| References and rules (protected paths) | Q-12 | M3 |
| Verification and CI status | Q-15 | M3 |
| Task boundaries (diff hygiene) | Q-16 | M3 |
| api-diff wrappers | Q-10 | M4 |
| Semgrep/CodeQL rule packages | Q-17, Q-18 | M4 |
| Strict config profiles and per-language dictionaries | Q-01/Q-02/Q-03 | M4, then continuous |

**Out of scope:** Q-01…Q-09 as such (they are wrappers over ready-made tools, assembled from the profiles), rewriting the tools, automatic fixes (the gates only detect and report), automatic merges.

## 2. The reference model of the target repository's environment

The scripts may rely on the presence of (see `QUALITY_GATES.md` §1.5, L0):

- `EXCEPTIONS.md` at the root — the E-C exception registry: `### EX-YYYY-NNN` blocks with the fields "Principle", "Scope", "Essence of the deviation", "Justification", "Compensating controls", "Sign-off", "Review deadline" (a date), "Status";
- `baseline/suppressions.yaml` — the suppression baseline (the format — GUIDELINE_profiles_and_dictionaries §1);
- `REPO_CLASS` — repository/module classes, the standard version, a link to the critical-modules manifest;
- the critical-modules manifest and the protected-paths list (golden files, formula modules) — in the gates' config;
- CODEOWNERS covering all the listed files.

## 3. Requirements per gate

### 3.1. Q-11 "Suppressions and gate configurations" (blocker)

**Input:** the git diff `base…head`, `baseline/suppressions.yaml`, `EXCEPTIONS.md`, the suppression dictionary (per ecosystems), the parsers of effective linter configurations.
**Logic:**
1. Extract suppressions from the diff (added lines only; removed ones are not counted) by the pattern dictionary.
2. For every new suppression: a reason comment present; a valid `EX-…` ID from the registry; the review deadline not expired. Absence/expiry — FAIL.
3. Compare the suppression count (by kind) against the baseline: growth — FAIL. **Compensation is prohibited** ("+3 new / −4 old" — FAIL).
4. More than 3 suppressions per PR → a second-reviewer requirement (a label + `mergeable=false` until approval from CODEOWNERS).
5. A diff of the **effective** tool configuration (parsed canonical JSON, not the config text) or the appearance of a new tool config file in the tree (including nested directories) → a forced `gates-change` label.
6. The PR touches both baseline files and code → FAIL (`baseline-reset` — a separate PR only).
7. Removing lines with suppressions does NOT decrease the baseline automatically: the baseline migration — only by the tool (`gate-runner baseline migrate`) on mechanical PRs.

**Acceptance scenarios:** Б-1, Б-2, Б-3, Б-5, Б-6, Б-7, Б-8, Б-10 (section 5).

### 3.2. Q-19 "The exceptions and classes audit" (blocker, nightly)

**Input:** the whole repository tree, `EXCEPTIONS.md`, `REPO_CLASS`, dates from CI.
**Logic:**
1. Collect `EX-\d{4}-\d{3}` anchors in code/configs; verify against the registry: an anchor without a record or a record without an anchor → FAIL (an anchor older than 1 business day without a record — FAIL unconditionally).
2. Expired "Review deadlines" → FAIL for the affected files (in the PR) and an entry in the nightly report.
3. Grouping E-C by (principle, cause): ≥3 matches → auto-creating a task "A PR to the standard (E-D)" via the tracker API, with an alert template.
4. The К3 code share (per `REPO_CLASS`) and its change since the previous run → an alert to the standard's owner.

**Acceptance scenarios:** Б-3, Б-17, Б-18, Б-19, Б-20.

### 3.3. Q-12 "References and rules"

**Input:** the diff, the protected-paths config (sources: CODEOWNERS + `REPO_CLASS`).
**Logic:** the diff touches a protected path → the `rule-change` label + a mandatory reviewer from CODEOWNERS; an intersection with Q-11 → both labels + the highest sign-off; a **new** golden/snapshot file in the same PR where its module's code changes → enhanced review (a flag); for К1 — a semantic signal: a change of numeric literals in modules from the "calculation" list → a warning annotation.

**Acceptance scenarios:** Б-9, Б-11, Б-12 (label intersection).

### 3.4. Q-15 "Verification and CI status"

**Input:** the PR text (only as an object of inspection, not as a source of truth), the required-check statuses (the CI API), the run/artifact references mentioned in the PR, the list of commands from the repository's scripts/configs.
**Logic:**
1. Textual success markers ("tests pass", "the build is fine", and the marker dictionary from the config) with a red required check → FAIL.
2. References to runs/artifacts: must exist in the CI API and belong to this commit/PR → otherwise FAIL.
3. The mentioned verification commands must exist in the repository's scripts/configuration → otherwise FAIL.
4. The "session stop events" field absent from the filled PR template → a warning (not FAIL: template filling is procedural).

**Acceptance scenarios:** Б-15, Б-16.

### 3.5. Q-16 "Task boundaries"

**Input:** the task ID from the branch name/PR title, the task's file list (the tracker API), the diff, the "mechanical changes" config.
**Logic:**
1. The task's file list not found in the tracker → status **SKIP** (explicitly in the report, not a silent skip).
2. The affected files ⊆ the task's list → OK; outside the list → FAIL (the `scope-violation` label).
3. A diff > 600 lines outside mechanical changes (the definition — `ENGINEERING_PRINCIPLES.md` §0.7) → a warning annotation.
4. Per-subject aggregates (PRs/suppressions/guard labels per period) → above the threshold — an escalation task (see `EXCEPTIONS_POLICY.md` §8).

**Acceptance scenarios:** Б-13, Б-14.

### 3.6. Q-10 "api-diff" (a wrapper)

**Input:** base/head, the per-language tools config (api-diff, rustdoc-json, oasdiff, protobuf detectors).
**Logic:** run the tool; the tool's findings → the `api-change`/`breaking` labels (set by the bot); for a language without a tool → status **UNAVAILABLE** (not a silent OK).

**Acceptance scenarios:** Б-21.

### 3.7. Q-17/Q-18 — rule packages (not code: rules + tests)

Semgrep/CodeQL rule sets per language:
- **Q-17:** an HTTP client without a `timeout`, a socket/stream read without a limit, a DB query without a timeout (a minimum of 8–12 rules per primary language).
- **Q-18:** recursion in a module processing external data without an explicit depth bound; a stream-reading loop without a maximum counter (a minimum of 4–6 rules).

Every rule — with a positive/negative fixture. Mode: К1 — blocking; К2 — warning (configurable in the profile).

## 4. Non-functional requirements

1. **Determinism:** two runs on the same commit produce identical reports (no timestamps in the compared fields).
2. **Outcome modes:** `OK | FAIL | SKIP | UNAVAILABLE` — explicit; SKIP/UNAVAILABLE are recorded in the report with a reason. Fail-closed for security gates (Q-07-adjacent paths), fail-explicit for the rest: the tracker/CI API being unavailable — `UNAVAILABLE`, never a silent OK.
3. **Performance:** PR gates ≤ 60 s for a repository of ≤ 100k files; Q-19 ≤ 15 min (nightly). Diff-oriented, no full re-analysis.
4. **Security:** the scripts do not execute the target repository's code (they only parse it); the repository's content is treated as data (anti-injection: strings from code/configs are never interpreted as commands or execution paths); path checks against symlink escape; CI tokens — minimal scope (PR labels + read).
5. **Versioning:** the runner and the gates are versioned; target repositories pin the version (a SHA is better); the baseline and report formats — with a `schema: N` schema.
6. **The report:** a machine-readable JSON (the schema below) + human-readable annotations; the JSON schema is versioned.

```json
{
  "schema": 1,
  "gate": "Q-11",
  "gate_version": "1.0.0",
  "status": "FAIL | OK | SKIP | UNAVAILABLE",
  "reason": "a string for SKIP/UNAVAILABLE",
  "findings": [
    {"code": "SUPPRESS_NO_EXID", "severity": "error",
     "path": "src/x.py", "line": 42, "message": "…", "evidence": "…"}
  ],
  "labels": ["gates-change"],
  "second_reviewer_required": false,
  "stats": {"suppressions_new": 4, "baseline_total": 57}
}
```

7. **Compliance with one's own standard:** the companion repository is class К2; all gates apply to it, including its own Q-11 (it gates itself with its own dictionary).

## 5. The acceptance (bypass) scenario matrix

Every scenario — a fixture: a mini-repository (base/head git snapshots) + expected findings. Acceptance = all scenarios green on the reference data **and red on the bypass scenarios**.

| # | Scenario | Expectation | Gate |
|---|---|---|---|
| Б-1 | 30 suppressions, the PR claims "30" | FAIL: comparison against the baseline, not the claim | Q-11 |
| Б-2 | A suppression without a reason or an EX-ID | FAIL | Q-11 |
| Б-3 | A suppression with an expired/foreign EX-ID | FAIL | Q-11, Q-19 |
| Б-4 | The diff changes a CI-workflow file | the `gates-change` label | Q-11 |
| Б-5 | A nested `.eslintrc` in a subdirectory | the `gates-change` label | Q-11 |
| Б-6 | A threshold changed inside an existing config | the `gates-change` label (fingerprint) | Q-11 |
| Б-7 | baseline + code in one PR | FAIL | Q-11 |
| Б-8 | −4 old / +3 new suppressions | FAIL: compensation prohibited | Q-11 |
| Б-9 | A test deleted, checks weakened | `test-change` + a second review | Q-12/wiring |
| Б-10 | A module renamed with violations carried over | the baseline migrates by tool, is not zeroed | Q-11 |
| Б-11 | A new golden file in a PR with a code change | enhanced review | Q-12 |
| Б-12 | golden+config intersecting in one file | both labels + the highest sign-off | Q-11+Q-12 |
| Б-13 | No file list in the task | SKIP with an explicit reason | Q-16 |
| Б-14 | Files outside the task's list | FAIL | Q-16 |
| Б-15 | "Tests pass" with red CI | FAIL | Q-15 |
| Б-16 | A reference to someone else's run ID | FAIL | Q-15 |
| Б-17 | An EX anchor without a registry record (>1 business day) | FAIL | Q-19 |
| Б-18 | 3+ exceptions of one principle/cause | an auto E-D task | Q-19 |
| Б-19 | An expired exception | FAIL for the affected files | Q-19 |
| Б-20 | The К3 share grew | an alert to the owner | Q-19 |
| Б-21 | api-diff: breaking found | the `breaking` label | Q-10 |
| Б-22 | An HTTP call without a timeout (К1) | FAIL | Q-17 |
| Б-23 | A parser's recursion without a depth bound (К1) | FAIL | Q-18 |
| Б-24 | The same commit twice | identical reports | all |

## 6. Stages and acceptance criteria

| Stage | Contents | Acceptance criterion | Estimate |
|---|---|---|---|
| M1 | The runner skeleton: the gate contract, Findings, the JSON report, GitHub/GitLab adapters, the test infrastructure (runner fixtures) | a demo: a dummy gate passes the full CI→label→annotation cycle; the report schema approved by the standard's owner | 1 week |
| M2 | Q-11 + Q-19 | the scenarios Б-1…Б-3, Б-5…Б-8, Б-10, Б-17…Б-20; the repository gates itself with Q-11 | 2–3 weeks |
| M3 | Q-12, Q-15, Q-16 | the scenarios Б-9, Б-11…Б-16 | 2 weeks |
| M4 | Q-10 wrappers, the Q-17/Q-18 packages, the profiles of 2–3 of the organization's main stacks | the scenarios Б-21…Б-23; the profiles apply to freshly created projects of the stacks | 2 weeks |

**The package's overall acceptance criterion:** the full Б-1…Б-24 matrix; the standard-owner's review; the gates' documentation (a README per gate: input/output/config/limitations).

## 7. Definitions

"A critical module", "a mechanical change", "generated code", "a library", "the basic К3 set" — per `../../standards/ENGINEERING_PRINCIPLES.md` §0.7. "A suppression", "an effective configuration", the baseline and registry formats — per `GUIDELINE_profiles_and_dictionaries.md`.
