# QUALITY_GATES
## Automated checks and acceptance criteria

**Version:** 1.2 · **Purpose:** the executable enforcement model of the standard `ENGINEERING_PRINCIPLES.md`. The standard is enforced by the pipeline, not by instructions in an agent's prompt. Some rules are procedural (enforced by review and process artifacts); they are explicitly marked, and their share is published as the maturity metric (§6).
**Official translation.** The authoritative text is the Russian original (`standards/QUALITY_GATES.md`); in case of divergence the Russian wording prevails. Classes: [MANDATORY] = [ОБЯЗ], [RECOMMENDED] = [РЕК], [COND] = [УСЛ].

---

## 1. The enforcement model: four levels

The standard is enforced in echelons — the earlier a violation is caught, the cheaper the fix:

| Level | Mechanism | What it catches | Latency |
|---|---|---|---|
| **L0. Perimeter** | Hosting settings: branch protection, force-push ban, required status checks, CODEOWNERS on the standard's infrastructure (§1.5) | The guarantee that L1–L3 cannot be bypassed by a push to main or a checkbox in settings | constant |
| **L1. Instructions** | `AGENTS.md` / `CONTRIBUTING.md` at the repository root, referencing `AI_AGENT_RULES.md`; the PR template; the task template | Steering the agent's work, task boundaries | before code |
| **L2. Pre-commit** | Hooks: formatting, quick lint, secrets scan | Formatting errors, secrets, "forgot to lint". Hooks are bypassable (`--no-verify`) — everything critical is duplicated in L3 | seconds |
| **L3. PR gates** | CI on every PR: build matrix, lint/types/analysis, unit and integration tests, dependency audit, architecture tests, api-diff, coverage diff | All mechanically checkable requirements | minutes |
| **L4. Nightly/background** | Fuzzing, deep static analysis, benchmarks, load leak tests, audit of new CVEs in existing versions | Long and stochastic checks | hours |

**Key rule:** any rule of the standard that can be checked automatically must have a gate, **unless** the rule is deliberately classified as procedural with a recorded justification (the list — §5 and the final table of `ENGINEERING_PRINCIPLES.md`). "Not mechanical" must be an explicit decision, not a default.

## 1.5. L0. Repository perimeter (mandatory hosting settings)

Mechanical enforcement exists only if it cannot be switched off from inside the repository. For К1/К2 the following are mandatory:

1. **Main-branch protection:** direct push is prohibited; changes — only via PR with required status checks; force-push and branch deletion — prohibited.
2. **CODEOWNERS on the standard's infrastructure** (protected paths): CI configurations (`workflows/`), linter/type/analyzer configs, ratchet baseline files, `EXCEPTIONS.md`, `REPO_CLASS`, `AGENTS.md`, the PR template, `CODEOWNERS`, the manifest of critical modules. The owner is the standard's owner.
3. **Review — humans only.** An agent cannot approve a PR (neither its own nor another agent's). For `gates-change`/`rule-change`/breaking labels — CODEOWNERS plus at least one human reviewer. If the organization allows an agent reviewer: a different vendor/model, no self-review of its own work, mandatory Q-10/Q-11/Q-12.
4. **Agent change modes:** by default the agent creates a draft PR; promotion to "ready for review" — after green CI and a human action. A confirmed H6 violation (verification faking) — demotion of the agent/author to "draft-only" mode pending investigation (see `EXCEPTIONS_POLICY.md` §8).
5. **No admin bypass** (or: admin merge bypassing gates — only as a "procedural deviation" with a record and a mandatory deferred full run, §6).
6. **Provenance marking:** agent commits carry the trailer `AI-Origin: <agent/model>` — for post-incident audit and per-subject metrics.

Recommended (not mandatory): signed commits; canary markers of `AGENTS.md` readership (1–2 verifiable behavioral requirements — e.g., the mandatory H9 report format; their absence in a PR = L1 not read, the bot rejects).

**The L0 rule:** without §1.5 in place, the standard is not considered adopted (`IMPLEMENTATION_GUIDE.md`, stage 3).

## 2. Project classes and strictness

Gates are configured per repository/module class (class definitions — `ENGINEERING_PRINCIPLES.md` §0.6):

| Gate | К1 (critical/production-grade) | К2 (production) | К3 (experimental) |
|---|---|---|---|
| Format/lint/types | blocking | blocking | blocking (basic set) |
| Static analysis | blocking + sanitizers | blocking | warning |
| Unit tests | blocking | blocking | blocking |
| Integration tests | blocking | blocking | if present |
| E2E | blocking (smoke) | blocking (smoke) | — |
| Coverage diff | blocking: ≥ 80% (branch) on changed code of critical modules | blocking: ≥ 70% (branch) on changed functions; global coverage — a non-blocking ratchet (alert on drift) | informational |
| Architecture tests | blocking | blocking | — |
| CVE audit | blocking (critical) | blocking (critical), deadline for the rest | weekly report |
| Secrets scan | blocking | blocking | blocking |
| api-diff | blocking | blocking for public surfaces | — |
| Benchmarks | blocking thresholds on budget paths | nightly + alerts | — |
| Fuzzing | nightly; targets = parsing points of untrusted data (the target list is fixed in the repository) | nightly (same targets) | — |

"The basic К3 set" is defined in `ENGINEERING_PRINCIPLES.md` §0.7 (carrier terms).

## 3. The ratchet rule

For existing repositories, "zero violations from day one" is unachievable, therefore:

1. **The baseline** is fixed at adoption (a snapshot of current violations per tool: counts per file/rule).
2. **Growth is prohibited:** a PR may not increase the number of violations of any kind. It may decrease them.
3. The baseline decreases monotonically; target levels — the adoption plan (`IMPLEMENTATION_GUIDE.md`).
4. Baseline decreases "by themselves" (without a PR) are prohibited — baselines change only via PRs with justification.
5. **No mutual compensation:** growth of any kind of violation in a PR is prohibited regardless of reductions; "+5 new against −6 fixed old ones" does not pass — a new category of violations is not compensated by fixing old ones.
6. **The baseline is a protected path:** baseline files are under the standard-owner's CODEOWNERS; a baseline change and code changes — in different PRs (a reset — the `baseline-reset` label); mechanical code movement (rename/generation) does not recompute the baseline by hand — the ratchet tool performs the migration.
7. **Enforced reduction:** an L4 job "a violation kind's baseline has not decreased for N months" — an alert to the owner with a mandatory plan.

Formally: `violations(new_code) ≤ violations(base) − improvements`. Tools: "new issues only" mode (reviewdog, golangci-lint `--new-from-rev`, ruff `--no-cache` + diff, mypy `--follow-imports=skip` + incremental baseline, etc.).

## 4. The gate catalog

Format: **ID · checks · tools (examples) · pass criterion · mode.**

### Q-01 Formatting
- Checks: uniformity of format (not substantive complexity).
- Tools: the ecosystem's formatter (gofmt, black/ruff format, prettier, rustfmt, clang-format, ktlint).
- Criterion: the diff after the formatter is empty.
- Mode: blocking, L2+L3.

### Q-02 Linter
- Checks: idioms, simple defects, domains A/D (A1, A6, B3, D3 partially).
- Tools: eslint+plugins, ruff/flake8, golangci-lint, clippy, cppcheck, clang-tidy, detekt, SpotBugs.
- Criterion: zero new findings (ratchet); the project's config = the standard's strict profile. **Complexity metrics (A4):** absolute thresholds — warning; for functions *modified* in the PR — a ratchet in blocking mode: exceeding a threshold requires an explicit justification checkbox in the PR template (presence is checked mechanically, quality — by review). Generated code is recognized by the generation config (§0.7 `ENGINEERING_PRINCIPLES.md`), not by a marker in the file header.
- Mode: blocking. The "fix the code, not the warning" rule (F2): suppression — only point-wise with a reason-ID comment; counted by gate Q-11.

### Q-03 Types
- Checks: D1 (contracts in types), F3.
- Tools: tsc `strict`, mypy `strict`, javac `-Xlint`, rustc (by default), compilers in warning-as-error mode (per ecosystem).
- Criterion: zero type errors; `any`/`unchecked` bypasses — only with local suppressions (counted by Q-11).
- Mode: blocking.

### Q-04 Unit and integration tests
- Checks: F1, D6 (boundary matrices), F6 (regressions).
- Criterion: all green; time budgets per test class (unit — minutes; integration — tens of minutes; e2e — configurable), a hang detector per class; flaky — quarantine only with an owner, a cause, and a deadline, with automatic return to blocking mode upon expiry.
- Mode: blocking, L3.

### Q-05 Coverage
- Checks: F1 — sufficiency of testing of critical modules.
- Criterion: **the diff policy.** К1: ≥ 80% branches on changed code of critical modules (the critical-modules manifest — a protected path, §0.7 `ENGINEERING_PRINCIPLES.md`). К2: ≥ 70% branches on changed functions; global coverage — a non-blocking ratchet (alert: > 0.5 pp drop per PR or > 2 pp per quarter). К3: informational. A global absolute threshold is not a gate (it encourages tests for the percentage's sake).
- Mode: blocking on the diff; global — informational.

### Q-06 Static analysis (deep)
- Checks: domains A/B/D deeper than the linter (data flow, leaks, races).
- Tools: CodeQL/Semgrep, Infer, clang static analyzer; sanitizers (ASan/UBSan/TSan) on test builds of C/C++/Rust; `go test -race`.
- Criterion: zero new findings (ratchet); for К1 — zero sanitizer findings in tests unconditionally.
- Mode: L3/L4.

### Q-07 Secrets
- Checks: G4.
- Tools: gitleaks/trufflehog, pre-commit + CI.
- Criterion: zero findings. **Not subject to the ratchet or exceptions**, except immediate rotation + history cleanup.
- Mode: always blocking.

### Q-08 Dependency audit
- Checks: G3, E5.
- Tools: osv-scanner, `npm audit`, `pip-audit`, `cargo audit`, OWASP Dependency-Check; license scan.
- Criterion: no critical CVEs; the rest — no growth + a deadline; lockfile committed; new dependencies — with justification in the PR description.
- Mode: blocking (by class), L3 + weekly.

### Q-09 Architecture tests
- Checks: E1, E3 (dependency directions, cycles), A6 (export of mutable globals — where expressible).
- Tools: ArchUnit, dependency-cruiser, eslint-plugin-boundaries, import-linter, jdeps, go list scripts.
- Criterion: the import graph matches the repository's `ARCHITECTURE.md` declaration; no cycles.
- Additionally: an interface/trait/abstract class with a single implementation in *new* К1/К2 code — blocked as a speculative abstraction (E2/H2), unless it has a test substitute or a strategic-point mark in `ARCHITECTURE.md`.
- Mode: blocking for К1/К2.

### Q-10 API diff and compatibility
- Checks: H3, E4, E7.
- Tools: api-diff (Kotlin/Java), rustdoc-json diff, `git diff --stat` over public exports, protobuf/openapi breaking detectors.
- Criterion: a change of the public surface requires a "Contract changes" section in the PR; breaking — a second reviewer. The `api-change`/`breaking` labels are set by a bot from api-diff results, not by the PR author.
- Mode: blocking for libraries/platforms.

### Q-11 Suppressions and gate configurations (guard gate)
- Checks: H4, F2.
- Criterion: (1) the number of suppressions in the diff is compared against the **ratchet baseline**, not against the number declared by the PR author (self-reporting is not a data source for the gate); (2) every new suppression comes with a reason comment and a valid `EX-…` ID from `EXCEPTIONS.md` (a suppression without a valid EX-ID — red; mechanical linkage with the registry); (3) more than 3 suppressions per PR — a second reviewer; (4) a diff of the **effective** tool configuration (a parsed config, not a list of paths) and the appearance of any new tool config file in the tree, including nested subdirectory configs, — the `gates-change` label is set forcibly by the bot; (5) baseline files — under CODEOWNERS; a baseline change and code changes — in different PRs (`baseline-reset`).
- The suppression dictionary is a versioned gate config with its own contract test; the minimum: `noqa`, `nolint`, `# type: ignore`, `@ts-ignore`/`@ts-expect-error`/`@ts-nocheck`, `noinspection`, `#[allow]` (including crate-level), `@SuppressWarnings`, `eslint-disable`, `as any`, `unsafe`, `pytest.mark.skip|xfail|skipif`, `ignore_errors`, per-file-ignores and tool exclude paths.
- Mode: blocking.

### Q-12 Changes to references and rules (guard gate)
- Checks: H8, H5.
- Criterion: a diff of golden files, formulas, or tariff tables requires the `rule-change` label (set by the bot from the protected-paths list), the CODEOWNERS owner, and a second reviewer. A file under several guard gates — all applicable labels and the sign-off of the highest per §5 `EXCEPTIONS_POLICY.md`. New golden/snapshot files in the same PR as a code change — enhanced review (an agent does not appoint itself the oracle). К1 recommendation: semantic signals (changes of numeric literals in calculation modules).
- Mode: blocking.

### Q-13 Benchmarks and performance regressions
- Checks: C6, B5, F7.
- Criterion: budget paths — p50/p99 tracking in nightly runs; an alert at > +20% over the 7-day average (threshold configurable). For PRs touching budget paths, a benchmark CI job is mandatory; "before/after" measurements — a link to a run artifact, not "numbers in the description"; the `perf` label is set by the bot from the budget-path diff.
- Mode: alert + blocking only for К1 budget paths.

### Q-14 Fuzzing
- Checks: F5.
- Criterion: nightly parser targets; a crash = a task with a minimal reproducing input, which is added to the unit tests (F6) before closure. Closing the task without a regression test — only with an active E-C deviation "not expressible as a test" (F6: a record in `EXCEPTIONS.md` with an `EX-…` ID and a deadline); the anchor and deadline are visible to Q-19.
- Mode: L4, blocking on a found crash (via the task).

### Q-15 Verification and CI status
- Checks: H6, H9.
- Criterion: (1) merge — only with green CI; the status source — CI only; (2) a claim about a CI-covered check ("tests pass", "it builds") while CI is red — a red PR (mechanical detection); (3) for checks outside the pipeline — a link to a reproducible artifact (run ID / command + output hash / a re-runnable script); mentioned commands must exist in the repository's configuration/scripts — verified by the bot; (4) the PR template contains the author's checklist (single source — `AI_AGENT_RULES.md`) and a "session stop events" field.
- Mode: procedural + automatic sub-gates (2)–(3).

### Q-16 Diff hygiene and task boundaries
- Checks: H1.
- Criterion: (1) the list of expected files is taken from the tracker by the task ID in the branch/PR title — not from the PR description; if the list is absent from the task, the gate does not apply (stated explicitly), a signal mode remains; (2) "mechanical changes" — per the definition in §0.7 `ENGINEERING_PRINCIPLES.md`; (3) a diff > 600 lines outside mechanical ones — a signal to the reviewer; (4) per-subject aggregates (number of PRs/suppressions/guard labels per period) — against "salami-slicing" erosion in small portions (see `EXCEPTIONS_POLICY.md` §8).
- Mode: signal + procedural.

### Q-17 Timeouts and limits of external interactions
- Checks: B6, G6 (partially).
- Criterion: static rules for known patterns of external calls without a timeout/limit (an HTTP client without a timeout, a socket/stream read without a limit, a DB query without a timeout). Default values — the matrix in `ENGINEERING_PRINCIPLES.md` B6; the gate checks for an explicit limit, not a specific number. Partial mechanics — review provides completeness.
- Tools: the project's Semgrep/CodeQL rules.
- Mode: К1 — blocking; К2 — warning.

### Q-18 Recursion and loops over external data
- Checks: A2, A3 (partially).
- Criterion: static rules: recursion in a module processing external data without a visible depth bound; a stream-reading loop without an explicit maximum. The default limit (64) and the override rule — `ENGINEERING_PRINCIPLES.md` A2. Partial mechanics — review checks completeness (the A2/A3 checklist).
- Tools: Semgrep/CodeQL, linters.
- Mode: К1 — blocking; К2 — warning.

### Q-19 Audit of exceptions and project classes
- Checks: `EXCEPTIONS_POLICY.md` §6–7; `REPO_CLASS`.
- Criterion: a weekly L4 job: (1) `EX-…` anchors in code are verified against the `EXCEPTIONS.md` registry — a mismatch (including unregistered "urgent" deviations older than 1 business day) — red; (2) expired exceptions — a red flag for the affected files; (3) ≥ 3 exceptions of one principle with one cause — an automatic task for a PR to the standard (E-D); (4) the К3 share against the profile limit (default ≤ 20% — §0.6 `ENGINEERING_PRINCIPLES.md`): ≥ 16% — an alert to the standard's owner, above the limit — red; a PR changing code and `REPO_CLASS` at once — red (downward reclassification — a separate PR, see §0.6).
- Mode: L4; red flags on items (1)–(2).

## 5. Mechanically checkable vs requiring judgment

| Automatically checkable (gates) | Requires engineering judgment (review) |
|---|---|
| Format, lint, types, warning-free compilation (Q-01…03) | Meaningfulness of contracts and boundaries (D1) |
| Tests green, timeouts, flaky statistics (Q-04) | Adequacy of the boundary matrix (D6) |
| Diff coverage (Q-05) | Test quality: what exactly they check (not "coverage for the percentage's sake") |
| Sanitizers, races (Q-06) | Correctness of the memory strategy (B1) |
| Secrets, CVEs, lockfile (Q-07, Q-08) | Justification of a new dependency (E5) |
| Import directions, cycles (Q-09) | Sensibleness of module boundaries, speculative abstractions (E2) |
| API diff, breaking (Q-10) | Acceptability of a contract change (E7) |
| Suppressions vs baseline, EX-ID, gate configs (Q-11) | Falseness of a specific finding (Q-11, part 2) |
| EX anchors vs registry, expiries, К3 share (Q-19) | Validity of a specific exception (EXCEPTIONS_POLICY) |
| A reference diff requires labels/owner (Q-12) | Correctness of a *new* reference (H8) |
| Benchmark thresholds (Q-13) | The cause of a regression and an adequate response (C5) |
| Fuzzer crashes (Q-14) | CVE applicability to the configuration (Q-08) |
| Timeouts/limits: known patterns (Q-17) | Completeness of external-call coverage (B6) |
| Recursion/loops: known patterns (Q-18) | Provability of a bound in a specific case (A2/A3) |
| Verification log filled, CI green (Q-15) | Sufficiency of verification for the task's risk |
| Diff size/composition (Q-16) | The real task boundary (H1) |

**The design norm:** if a rule cannot be automated, it is formulated in the review checklist as one verifiable question — and remains a question, not a "moral obligation".

## 6. Agent stop conditions and enforcement honesty

The list of stop conditions has a single source: `AI_AGENT_RULES.md` §6 (no duplicate here — E6 applies to the standard itself). Two levels of enforcement:

**Mechanically backed** (bypass = red gate; the "stop" does not depend on the agent's good will): a public API/schema change (Q-10), an edit of references/rules (Q-12), a new dependency (Q-08), suppressions/gate configurations (Q-11).

**Procedural** (requirement ambiguity, test failures outside task boundaries, verification impossibility) — controlled by process artifacts:
- a mandatory PR/task field "session stop events": a list with `[STOP: <condition>]` markers or "none";
- the stop artifact: task status `question` + an assigned owner + a response deadline (SLA); merging in the `question` state is blocked;
- the list of failed tests and re-runs is recorded in the PR; the bot cross-checks the CI run history ("red → green without a code change" — a signal);
- the "reversible assumption" criterion is formal: it does not change the public surface/data/references (detected by Q-10/Q-12) and stays within the task's file limit.

**The maturity metric:** the share of `[MANDATORY]` rules enforced mechanically is published alongside the standard; rules without mechanics are explicitly marked "procedural" in the final table of `ENGINEERING_PRINCIPLES.md`.

**Policy for unavailable / infrastructurally red CI:** merge prohibited; legitimate paths — (a) freeze until restoration, (b) a procedural deviation with a sign-off per §5 `EXCEPTIONS_POLICY.md` and a mandatory deferred full run. An admin merge "around" without a record — a process violation.

## 7. The review checklist (non-mechanical requirements)

The author's checklist is not duplicated here: it lives in the PR template, single source — `AI_AGENT_RULES.md`. The review minimum — one verifiable question per rule (the §5 norm).

**Non-mechanical rules checkable only by a human:**

```
[ ] Task boundaries: everything touched is really needed for the task; no incidental changes (H1, Q-16)
[ ] No speculative abstractions: a new interface has a second implementation or a test substitute now (E2/H2, Q-09 signal)
[ ] Tests check behavior, not implementation; no weakenings or "bending" (H5, Q-12)
[ ] Assumptions from the task confirmed by the owner; no silent assumptions (H7)
[ ] The report is complete and honest: facts/expectations separated, "not verified" named, the stop-event log attached (H9, Q-15)
[ ] Optimization — only for a measured problem; a "before/after" measurement exists (C4/C5, Q-13)
[ ] The interface has no fictitious "second implementation" for the checkbox's sake (E2)
```

**Additionally (the remaining non-mechanical rules):**

```
[ ] Contracts are visible in signatures/types; the boundary matrix is adequate (D1, D6)
[ ] Errors are handled meaningfully; timeouts/limits on all external calls (D2, B6)
[ ] Complexity thresholds exceeded deliberately, with justification in the PR (A4)
```

## 8. The human reviewer: role, SLA, escalation

The human reviewer is a mandatory circuit of the standard: CI checks the mechanics (§5), the reviewer — judgment; duplicating the gates' work in review is prohibited. The existence of an attentive human review is an **explicit assumption** of the standard; additional rules of §1.5.3 apply to agent PRs (the agent-approval ban).

**SLA of the first substantive response on a PR** (business days):

| PR type | SLA |
|---|---|
| Regular | ≤ 2 days |
| Guard labels (`gates-change` / `rule-change` / breaking) | ≤ 1 day |

- Silence beyond the SLA → the author escalates to the standard's owner; the owner reviews personally or delegates — within 1 business day.
- A PR without a response for more than 5 business days — a signal into the process metrics (the aggregator — track D), **not** a basis for merging without review.
- Merging without non-mechanical review where it is required (guard labels, breaking, H-rules) — a process violation, not a "reviewer delay".
