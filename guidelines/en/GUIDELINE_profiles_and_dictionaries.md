# GUIDELINE: configuration profiles, suppression dictionaries, the Q-17/Q-18 rules

**Version:** 1.0 · Audience: the companion maintainer; anyone adding a new language/ecosystem.
**Official translation.** The authoritative text is the Russian original (`guidelines/GUIDELINE_profiles_and_dictionaries.md`); in case of divergence the Russian wording prevails. Pattern IDs, labels, and file paths are not translated.

---

## 1. The suppression dictionary (Q-11)

### 1.1. The format

`dictionaries/<ecosystem>.yaml`, the schema is versioned:

```yaml
schema: 1
ecosystem: python
patterns:
  - id: noqa                 # a stable suppression-kind id
    regex: '#\s*noqa(?::\s*(?P<codes>[A-Z0-9,]+))?'
    languages: [python]
  - id: type_ignore
    regex: '#\s*type:\s*ignore'
    languages: [python]
  - id: pytest_skip
    regex: '@pytest\.mark\.(skip|skipif|xfail)'
    languages: [python]
```

Mandatory categories (the minimum, from `QUALITY_GATES.md` Q-11): `noqa`/`flake8`, `nolint`, `# type: ignore` + `pyright: ignore`, `@ts-ignore`/`@ts-expect-error`/`@ts-nocheck`, `noinspection`, `#[allow]` (including `#![allow]` crate-level), `@SuppressWarnings`, `eslint-disable` (+ per-line/per-file forms), `as any`, `unsafe` (Rust), `pytest.mark.skip|xfail|skipif`, `@Ignore`/`@Disabled` (JUnit), `ignore_errors` (mypy per-module), per-file-ignores and tool exclude paths (a separate `path_excludes` category).

### 1.2. Maintenance rules

1. **Pattern ids are stable** — the baseline references them; renaming an id = a baseline migration (by the `gate-runner baseline migrate` tool), not a hand edit.
2. **The dictionary's test contract:** for every `id` — a fixture file with a positive and a negative example; a dictionary without a fixture does not pass the companion's CI.
3. **A new pattern = a PR with a changelog entry** ("mechanism X added, found in …"); silent expansion is prohibited — otherwise the dictionary itself becomes a channel of weakening.
4. The reason comment and the `EX-…` ID are looked for **on the same line or the line above** the suppression (configurable per id: `reason_proximity: same_line | line_above`).

### 1.3. The target repository's baseline file

```yaml
# baseline/suppressions.yaml
schema: 1
counts:                      # suppression kind -> glob -> maximum allowed
  python/noqa:      { "src/**": 12, "tests/**": 40 }
  python/type_ignore:{ "src/legacy/**": 5 }
fingerprint:                 # the last fixed effective configuration
  eslint: { "eslint.config.mjs": "sha256:…" }
generated_at: 2026-11-14T00:00:00Z
generated_by: gate-runner 1.x
```

Rules: growth of any counter → FAIL; a decrease is allowed (a PR may introduce it); the file is under the standard-owner's CODEOWNERS; a baseline change and code changes — different PRs (`baseline-reset`).

## 2. Config fingerprint (detecting config "softening")

For every supported linter — a parser module returning the **canonical JSON of the effective rules**: enabled rules, levels, thresholds, ignore paths. The fingerprint = SHA-256 of the canonical JSON. The baseline stores the latest fingerprints; any divergence or a new tool config file in the tree → `gates-change`.

The minimal parser set at the start: ESLint (flat + legacy JSON), ruff/flake8 (pyproject/setup.cfg), golangci-lint, mypy (incl. per-module overrides), tsc (tsconfig), clippy (Cargo.toml `[lints]` + clippy.toml), clang-tidy (.clang-tidy). For script configs (`.eslintrc.js`) — we parse JSON-like shapes; the limitation is noted in the parser's README.

## 3. Strict profiles (Q-01/Q-02/Q-03)

`profiles/<lang>/` — ready-made "maximum strictness" configs for a fresh project:

| Language | Profile contents |
|---|---|
| Python | `ruff.toml` (the full set + `select: ALL` minus documented disputable rules), `mypy.ini` strict, a bandit-class semgrep set |
| TypeScript | `tsconfig` strict (+ noUncheckedIndexedAccess), `eslint.config` strict-typescript, `any` banned without a suppress path |
| Go | `golangci-lint.yml`: vet, errcheck, staticcheck, gocyclo/funlen in warning mode |
| Rust | `Cargo.toml [lints]` clippy pedantic-minus-disputable, `#![deny(warnings)]` for lib crates |
| C/C++ | `.clang-tidy` (core, bugprone, concurrency), the flags `-Wall -Wextra -Wpedantic -Werror`, sanitizer configs for tests |
| Java/Kotlin | ErrorProne + detekt/ktlint strict config |

Maintenance rules: every profile has an owner; a test "the profile is applied to a freshly created project of the stack and builds without errors"; disputable exclusions — with a reason comment right in the config (the configs themselves pass the companion's own Q-11 gate).

## 4. The Semgrep rules for Q-17/Q-18

### 4.1. Structure

`semgrep/q17-timeouts/<lang>/*.yaml` — every rule: an id (`q17-http-no-timeout`), severity per project class (set by a profile variable), a message with a link to the principle (B6), a fix hint.

### 4.2. Examples (Python)

```yaml
- id: q17-requests-no-timeout
  message: "B6/Q-17: an HTTP request without a timeout - an external interaction must have a limit"
  severity: ERROR
  languages: [python]
  patterns:
    - pattern-either:
        - pattern: requests.get($URL, ...)
        - pattern: requests.post($URL, ...)
    - pattern-not: requests.$M($URL, ..., timeout=$T, ...)
```

```yaml
- id: q18-recursion-no-depth
  message: "A2/Q-18: recursion over external data without a depth bound"
  severity: ERROR
  languages: [python]
  patterns:
    - pattern: |
        def $F(..., $DEPTH, ...):
            ...
            $F(..., $DEPTH + 1, ...)
```

### 4.3. Requirements for a rule package

1. Every rule — a **positive and a negative fixture** (code that is caught; code that must not be caught) — the companion's CI runs `semgrep --test`.
2. The rule marks the covered principle (B6/A2/A3) — for tracing in the report.
3. Broad-catch `pattern-regex` rules producing > 5% false positives on real-repo fixtures are prohibited (measured at addition time).
4. The minimum volume per primary language: Q-17 — 8–12 rules, Q-18 — 4–6.

## 5. api-diff tools (Q-10)

| Ecosystem | Tool | What it compares |
|---|---|---|
| JVM | kotlin-api-diff / japicmp / revapi | a jar/module against a base version |
| Rust | `cargo public-api` + diff | the public surface |
| Go | `go-apidiff` | packages/functions |
| Python | `griffe`/`pyapi-advisory`-style approaches + own | module exports (limitation: no strict types — noted in the report) |
| TS/JS | api-extractor + api-diff | the d.ts surface |
| Protobuf/OpenAPI | buf breaking / oasdiff | schemas |

No tool for a language = `UNAVAILABLE` of gate Q-10 with an explicit record (not a silent OK).

## 6. The procedure for adding a new language/ecosystem

1. Open a task in the companion with a checklist: a suppression dictionary + fixtures; a config-fingerprint parser; a linter/type profile; Q-17/Q-18 rules (if applicable); an api-diff tool (if applicable); an entry in the README's stack matrix.
2. Every artifact — via a PR with tests (the dictionary contract, semgrep --test, the profile on a fresh project).
3. Changes that weaken checks (deleting a rule, lowering a level) — the `gates-change` label and the standard's owner as reviewer (the companion's own Q-11 applies to it).

## 7. What must not be done

- Adding patterns/rules "just in case" that produce noise: false positives kill trust in gates faster than misses.
- Editing a target repository's baseline by hand: only via `gate-runner baseline` (a migration on mechanical moves) or a `baseline-reset` PR.
- Storing target-repository data in the companion (code, reports with file contents) — aggregates and metrics only.
- Weakening a profile "because the project is old": for that there is the target repository's ratchet, not a profile downgrade.
