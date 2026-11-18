# IMPLEMENTATION_GUIDE
## Adopting the standard in an existing repository

**Version:** 1.2 · **Purpose:** the practical procedure for adopting `ENGINEERING_PRINCIPLES.md` in a living project without a "big bang".
**Official translation.** The authoritative text is the Russian original (`standards/IMPLEMENTATION_GUIDE.md`); in case of divergence the Russian wording prevails.

---

## 0. The main principle of adoption

The standard is adopted **through gates, not through a discipline campaign**. The order is always the same: measure → fix the baseline → forbid growth → decrease the baseline gradually. An attempt to "fix everything at once" produces thousands of commits with no review value and sabotages trust in the pipeline.

## 1. Adoption stages

### Stage 1. Classification (1 day)
- Assign the repository a class К1/К2/К3 (`ENGINEERING_PRINCIPLES.md` §0.6); if heterogeneous — classes per module.
- Create `REPO_CLASS`: repository/module classes, the standard version, a link to the critical-modules manifest — under the standard-owner's CODEOWNERS.
- Assign the standard's owner in the repository (the one who signs off exceptions and gate configurations).

### Stage 2. The baseline snapshot (1–3 days)
- Run the full tool set in "report-only" mode: the format diff, the linter, types, static analysis, the dependency audit, the secrets scan, complexity metrics, coverage.
- Fix the results in the ratchet config (see `QUALITY_GATES.md` §3). This is the starting point — not a verdict.
- Separately: the secrets scan is **not** part of the ratchet — findings are fixed immediately (rotation + history sanitization).
- Baseline files — under the standard-owner's CODEOWNERS; a baseline reset — a separate PR with the `baseline-reset` label.

### Stage 3. The minimal working pipeline (2–5 days)
Enable in CI the blocking gates that are cheap and produce almost no false findings:
1. Formatter + linter on the diff (new findings only).
2. Types (strict mode on new modules; on existing ones — by the ratchet).
3. Unit tests + timeouts.
4. Secrets scan (full, blocking, no exceptions).
5. CVE audit (blocking for critical).
6. A PR template with the author's checklist, a "session stop events" field, and the verification rules (Q-15).

**L0 first.** Complete `QUALITY_GATES.md` §1.5: branch protection, the force-push ban, required status checks, CODEOWNERS on the standard's infrastructure, the agent-approval ban. **Without L0 the standard is not considered adopted** — the whole L3 can be switched off by a checkbox in the hosting settings.

**On pre-commit.** L2 is mandatory for К1/К2; the hooks config — in the repository. Local bypass via `--no-verify` cannot be prevented, therefore everything critical from L2 is duplicated in L3: the pipeline does not depend on local hooks. The agent is prohibited from using `--no-verify` without explicit permission in the task.

**On guard gates.** Q-10…Q-12, Q-19 — custom CI scripts; no ready-made tools exist for them; use the standard's companion (the gate implementations + strict per-language configuration profiles) or budget resources for writing them — this is the layer where adoptions usually stall.

### Stage 4. Instructions for agents and humans (1 day)
- `AGENTS.md` (or an equivalent) at the root: a link to `AI_AGENT_RULES.md` + stop conditions + a link to `EXCEPTIONS_POLICY.md`.
- A task template with an "Assumptions" field.
- A section in `CONTRIBUTING.md`: the brief exceptions procedure and a link to the gates.

### Stage 5. Architecture and contract gates (1–2 weeks, when ready)
- Fix the current dependency directions in `ARCHITECTURE.md` (describe what exists first, not what is "right").
- Enable the architecture tests (Q-09) in "no growth" mode: new cycles/directions prohibited, existing ones — in the baseline.
- For libraries/platforms — api-diff (Q-10) and the guard gates (Q-11, Q-12).

### Stage 6. Decreasing the baseline (continuously)
- Every principle with large debt gets an "owner" and a target level with a date.
- The reduction order by ROI: (1) swallowed/ignored errors, (2) timeouts/limits on external calls, (3) recursion over external data, (4) unhandled errors, (5) coverage of critical modules by tests, (6) the rest.
- Threshold metrics (A4): absolute thresholds — warning; a ratchet on modified functions — blocking with a justification checkbox (Q-02).

### Stage 7. Performance, fuzzing, and mutations (with budgets/parsers present)
- Define the budget paths (B5), add benchmarks (Q-13) and fuzzing targets (Q-14): the target list (parsers, protocol decoders, format handlers) is fixed in the repository.
- For К1 and critical modules — nightly spot checks of mutation testing (mutmut/Stryker/PIT/cargo-mutants) — a mechanical check of test strength.
- Without budgets — do not start (otherwise alert noise will kill trust).

## 2. The tools matrix (starter sets per language)

| Language | Format | Lint/types | Analysis/sanitizers | Tests | Security |
|---|---|---|---|---|---|
| C | clang-format | clang-tidy, cppcheck | ASan/UBSan/TSan, CodeQL | Unity/CMock, Criterion | gitleaks, osv |
| C++ | clang-format | clang-tidy, cppcheck | ASan/UBSan/TSan, CodeQL | GoogleTest/Catch2 | gitleaks, osv |
| Go | gofmt | golangci-lint, vet | `go test -race` | testing, testify | gitleaks, govulncheck |
| Java/Kotlin | ktlint/google-java-format | detekt, ErrorProne, SpotBugs | Infer, CodeQL | JUnit5, MockK | gitleaks, OWASP DC |
| JS/TS | prettier | eslint+types, tsc strict | Semgrep/CodeQL | vitest/jest, playwright | gitleaks, npm audit |
| Python | ruff format | ruff, mypy strict | Semgrep, bandit | pytest, hypothesis | gitleaks, pip-audit |
| Rust | rustfmt | clippy (strict) | miri/asan, cargo-fuzz | cargo test, proptest | gitleaks, cargo audit |
| C# | dotnet format | analyzers (strict), Roslyn | Roslyn analyzers + Semgrep/SonarQube in CI | xUnit/NUnit | gitleaks, osv |

Architecture tests: ArchUnit (JVM), dependency-cruiser / import-linter (JS/TS/Py), eslint-plugin-boundaries; for Go — custom scripts over a package list (no ready-made tool). For К1/К2 additionally: SBOM (syft/cyclonedx) in the release pipeline; api-diff — the ecosystem tools from the table.
Fuzzing: libFuzzer/AFL++ (C/C++), go-fuzz/stdlib fuzzing, cargo-fuzz, AFL-compatible wrappers for other languages.
A note: these are examples, not prescriptions; the rule is one — a tool is enabled by a gate from the catalog, not "out of thin air".

## 3. Adoption in agent workflows

- Keep the L1 instructions (`AGENTS.md`) short: the rules — in `AI_AGENT_RULES.md`, enforcement — in CI. An agent reading a 200-line rulebook executes it worse than an agent with 40 lines of rules and a hard pipeline.
- Give the agent access to running the gates locally (make/scripts) — then H6/H9 are executed for real.
- The guard gates (Q-11, Q-12) are mandatory for repositories with agent PRs: they turn "do not weaken checks" and "do not touch references" from an instruction into mechanics.
- Agent stops (stop conditions) are formalized by an artifact: the task status `question` + an owner + a deadline; the `[STOP: …]` markers; the stop-event log — a mandatory report field (`QUALITY_GATES.md` §6).
- A canary check: include 1–2 verifiable behavioral markers in `AGENTS.md` (e.g., the mandatory H9 report format) — the bot rejects a PR without them; a cheap detection of "the agent did not read L1".
- Agent commits — with the trailer `AI-Origin: <agent/model>`: incident audit, per-subject metrics, the agent-approval ban.

## 4. Adoption success metrics

- Time to green CI on a PR (target: < 15 minutes at unit level).
- The number of baseline violations (monotonically decreasing; the chart is visible to the team).
- The share of PRs with `exception`/`gates-change`/`rule-change` labels (low and not growing).
- Defects found by the gates before merge (the pipeline's usefulness — count and show it).
- The flaky share of tests (target: < 1%).
- Metrics against Goodhart's law: "the share of PRs with labels" is interpreted only together with absolutes (the number of suppressions per Q-11, the Q-19 results); "a low label share at a high number of suppressions" — a red flag.
- CI slower than 15 minutes — a pipeline incident: pipeline profiling, sharding, caching; slow CI is the main driver of gate sabotage.
- The share of mechanically enforced [MANDATORY] rules — the published maturity metric of the standard.

## 5. The prioritized adoption list (a summary)

1. **Secrets and CVE gates** (Q-07, Q-08) — cheap, huge risk, zero disputable findings.
2. **Format + lint + types on the diff** (Q-01…03) — the foundation of the ratchet.
3. **A PR template with the verification log and assumptions** (Q-15, H7/H6/H9) — agent discipline without code.
4. **Tests + timeouts + diff coverage** (Q-04, Q-05).
5. **Guard gates** (Q-11, Q-12) — protecting the pipeline from agents and deadlines.
6. **Architecture tests** (Q-09) — after fixing the actual architecture.
7. **api-diff** (Q-10) — for libraries/platforms.
8. **Benchmarks and fuzzing** (Q-13, Q-14) — only with budgets/parsers present.
9. **Debt reduction** in the ROI order of stage 6.
10. **Changing the standard by the exception signals** (EXCEPTIONS_POLICY §6) — a continuous cycle.

## 6. Adoption anti-patterns

- "Enable everything strict at once" → a storm of red CI → gates switched off → trust lost.
- "100% coverage as a gate" → mock tests, a slower pipeline.
- "Functions ≤ 60 lines as a blocking gate" → mechanical splitting (A4).
- "Rules only in the agent's prompt" → enforcement depends on the model's mood.
- "We update the baseline on Fridays so CI is green" → the ratchet turned into an elevator.
- "We file exceptions verbally in chat" → invisible debt: and no protocol is kept.
- "The pipeline got slow — move the checks to nighttime" → the feedback loop breaks, gates start being bypassed; pipeline speed is part of the standard (§4).

## 7. Rollback and emergency modes

- Disabling/weakening a gate — only via E-D: a PR to the configuration with the `gates-change` label, the sign-off — the standard's owner, a term of no more than one cycle, with a recorded cause.
- Emergency mode (a production incident): a procedural deviation with a sign-off per `EXCEPTIONS_POLICY.md` §5 + a mandatory deferred full run + a retrospective.
- Unavailable / red-for-infrastructure-reasons CI: merge prohibited; the paths — a freeze or the emergency mode (see above).
- Rolling back the adoption (the team is overloaded): reduce strictness only via E-D, one gate at a time, measuring the effect — not "switch everything off".

## 8. Migrating the standard's versions

The standard's version is fixed in the target repository's `REPO_CLASS` — a "subscription" to an edition. A new version's release is accompanied by a summary changelog (`CHANGELOG.md`) and a migration section in this document; a release without them is not a release.

**The migration window** (the time allowed for the transition after a release):
- a minor release — fixes, clarifications, new gates (e.g., v1.1 → v1.2): **3 months**;
- critical fixes (security, erroneous guarantees) and major versions (v1.x → v2.0): **up to 1 month**; for majors — support of both versions within the window and an old/new ID correspondence table in the changelog.

**The target repository's migration procedure:**
1. Read the summary changelog; note the items affecting your class/stack.
2. Bump the version in `REPO_CLASS` — in a separate PR (`REPO_CLASS` and code are not mixed, §0.6 `ENGINEERING_PRINCIPLES.md`).
3. Cross-check the §0.7 EP lists against the gate configs: budget paths, golden/snapshot references, calculation modules, parsing points of untrusted data, protected paths.
4. If limits/thresholds are overridden in the project's profile — cross-check against the new defaults (e.g., the B6 timeout matrix).
5. Run the gates; discrepancies — via E-D (`gates-change`), not silently.

Until the window closes, the old version is valid: requirements introduced after it are not enforced — and that is not a violation. After the window expires, working on an outdated version — a signal to the standard's owner.
