#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""digest_en.py — английские тексты для `build_digest.py --lang en`.

Официальный перевод (канон — русская редакция EP). Ключи — ID принципов
(A1…H9, включая слитые заглушки). Заголовок + дословный абзац «Требование».
Классы не переводятся в данных: преобразование классов и доменных заголовков —
в build_digest.py (CLASS_EN / DOMAIN_EN).

Правка русского текста EP не требует правки этого файла, пока не изменился
смысл требования; расхождение ловится ревью перевода.
"""

from __future__ import annotations

# Доменные заголовки: буква домена -> английский заголовок.
DOMAIN_EN: dict[str, str] = {
    "A": "Domain A. Control flow and program structure",
    "B": "Domain B. Memory and resource management",
    "C": "Domain C. Algorithms and performance",
    "D": "Domain D. Reliability and correctness",
    "E": "Domain E. Architecture and maintainability",
    "F": "Domain F. Testing and verification",
    "G": "Domain G. Security",
    "H": "Domain H. Requirements for AI development agents",
}

OUTSIDE = "(outside domains)"

# Классы: русский ярлык -> английский.
CLASS_EN: dict[str, str] = {
    "ОБЯЗ": "MANDATORY",
    "РЕК": "RECOMMENDED",
    "УСЛ": "COND",
}

MERGED_PREFIX = "слит"  # cls.startswith(MERGED_PREFIX) -> "merged into <tail>"
MERGED_EN = "merged into"

# ID -> (заголовок EN, требование EN). Заглушки — текст-указатель.
TEXT_EN: dict[str, tuple[str, str]] = {
    "A1": ("Simple and explicit control flow constructs",
           "Control is transferred only by explicit, top-down readable structures: sequence, branching, loops, calls, structured error handling. Prohibited: `setjmp`/`longjmp` and their analogues, unstructured jumps, hidden control-flow interception (monkey-patching, remote method substitution); `goto` — outside the centralized resource-cleanup pattern (see below); exceptions — only for exceptional situations, not as a regular control-transfer mechanism."),
    "A2": ("Bounded recursion",
           "Recursion is allowed only if the depth is bounded provably (by a data structure with a known maximum depth) or explicitly (a depth parameter + a protective limit). In К1 and in code without a guarantee of bounded input — iteration instead of recursion."),
    "A3": ("Explicit iteration bounds and runaway-loop protection",
           "Every loop either has a bound provable from the data structure (array length, collection size) or — if it iterates a potentially unbounded or external source — must have an explicit protective iteration limit (guard) and defined behavior when it is exceeded. Loops intended to be infinite (event loops, schedulers, servers) are allowed, but must demonstrate a progress guarantee or a timeout on every iteration."),
    "A4": ("Function and module complexity control — triggers, not dogmas",
           "Numeric complexity thresholds (function length, cyclomatic complexity, parameter count) are used as **triggers for mandatory explanation at review**, not as automatic gates and not as a measure of quality. Exceeding a threshold requires one or two sentences from the author on \"why this is better\", not mechanical splitting."),
    "A5": ("Explicit state transitions",
           "Merged into **A1** (\"Simple and explicit control flow constructs\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: explicit state machines moved into the survivor's \"How to comply\" section. The ID is kept for reference tracing."),
    "A6": ("Minimal scope and minimal shared mutable state",
           "Data is declared in the smallest sufficient scope. New mutable global variables, publicly mutable module fields, and mutable singletons are prohibited without explicit justification. Preference — immutable data."),
    "A7": ("Conditional compilation and feature-flag discipline",
           "The combinatorics of build and behavior variants is controlled explicitly: conditional compilation (`#ifdef`, build tags, build configs) is minimal, every variant is included in the CI matrix; feature flags have an owner, a removal deadline, and a test of both branches; \"eternal\" flags and flags without a test of the disabled branch are a defect."),
    "B1": ("Predictable and bounded memory consumption",
           "The memory-allocation strategy is determined by the system class and fixed explicitly. К1 (real-time/embedded): allocation only at initialization time or from pre-allocated pools; after initialization — no allocations (NASA rule 3 is preserved verbatim). К2: allocation is allowed but bounded — volumes are limited, collection growth has a cap, behavior under maximum load is predictable and verified. Memory and handle leaks are absent; copying large data unnecessarily without measurement is not allowed. (Absorbed B2 and B4 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)"),
    "B2": ("Frugal data creation and copying",
           "Merged into **B1** (\"Predictable and bounded memory consumption\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`. Content moved into the survivor's \"How to comply\" and \"Exceptions\" sections. The ID is kept for reference tracing."),
    "B3": ("Deterministic resource lifetime management",
           "The lifetime of every resource (files, sockets, connections, locks, transactions, subscriptions) is managed by a language mechanism of deterministic release: RAII / `using` / `try-with-resources` / `defer` / context manager. Manual release \"in the right place\" is prohibited as an approach."),
    "B4": ("Leak control",
           "Merged into **B1** (\"Predictable and bounded memory consumption\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`. Content (sanitizers on CI, memory stability under load, eviction of growing structures) moved into the survivor's \"How to comply\" and \"Automation\" sections. The ID is kept for reference tracing."),
    "B5": ("CPU/RAM/disk/network efficiency — by budget, not intuition",
           "For components whose resource consumption is a product property (request latency, on-device memory, mobile-app traffic), explicit budgets are defined; code is checked against budgets, not feelings. For components without such properties — \"fast enough\" and the no-premature-optimization rule (C4)."),
    "B6": ("Explicit resource limits on every external interaction",
           "Every interaction with the outside world (network, files, user input, inter-process communication) has explicit limits: a timeout, a maximum size, a maximum number of items/attempts — and defined behavior on exceeding them (error, request rejection, degradation). \"Wait as long as it takes\" and \"accept as much as comes\" are prohibited."),
    "C1": ("Deliberate complexity: algorithms, recomputation, data structures",
           "For operations over collections whose size grows with external data, complexity must be deliberate: the author understands and, when needed, documents it (e.g., \"O(n·m) is acceptable, m≤8\"). Accidental quadratic behavior on a user-controlled path is a defect. Loop-invariant computations are moved out of the loop; caching — only with a measured need and an eviction policy. The data structure is chosen by the dominant access pattern, not by habit. (Absorbed C2 and C3 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)"),
    "C2": ("Do not repeat computations needlessly",
           "Merged into **C1** (\"Deliberate complexity\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: loop-invariant extraction and memoization/cache discipline moved into the survivor's \"How to comply\" section. The ID is kept for reference tracing."),
    "C3": ("Appropriate data structures",
           "Merged into **C1** (\"Deliberate complexity\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: data-structure selection by access pattern moved into the survivor's \"How to comply\" section. The ID is kept for reference tracing."),
    "C4": ("No premature optimization",
           "No optimization without a problem: a measured degradation, an unmet budget, or a demonstrable asymptotic error (C1). Readability and simplicity are the default behavior. \"Optimizing just in case\" is a violation of the standard."),
    "C5": ("Profile before optimizing",
           "Substantial performance work starts with a profile on representative load. A PR with optimization contains \"before/after\" measurements (numbers, scenario, hardware/configuration). A patch that did not show an improvement under measurement is not accepted as an optimization."),
    "C6": ("Performance-regression protection",
           "For components with budgets (B5), automated benchmarks exist on critical paths, run regularly (at minimum — nightly), with alerts on threshold breaches. An alert is a signal to investigate, not to immediately \"make it faster\": first a profile (C5), then a decision (optimize / revise the budget / roll back)."),
    "D1": ("Explicit contracts: preconditions, postconditions, invariants",
           "Every non-trivial function has expressed contracts: preconditions and postconditions — via types (impossibility of an invalid value), assert checks, or brief documentation; structure invariants are concentrated in one place (methods of the type), not smeared across callers. Assert checks are free of side effects, boolean, with an explicit action on failure; meaningless checks (`assert(true)`, always-true conditions) are prohibited (at NASA — a direct requirement of rule 5)."),
    "D2": ("Input validation and explicit error handling",
           "Every input from the outside world (user input, network, files, broker messages, environment variables, CLI arguments, data from other services) is validated at system entry: schema/type/range/size — and either accepted in full or rejected with an explicit error. Inside the system after validation — trusted types. Errors are not silently ignored: every failure is handled meaningfully, logged with context, and propagated upward, or explicitly ignored via intentional-ignore syntax. (Absorbed D3 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)"),
    "D3": ("Complete and explicit error handling",
           "Merged into **D2** (\"Input validation and explicit error handling\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: error classification, `catch` discipline, and intentional-ignore syntax moved into the survivor's \"How to comply\" section (NASA r.7). The ID is kept for reference tracing."),
    "D4": ("Numerical correctness",
           "Numeric computations are performed correctly: floating-point comparison with a tolerance, operation order accounts for error accumulation, integer operations with overflow control where it is possible (external data, size arithmetic), NaN/Infinity do not propagate \"quietly\". For money — integer minor units or decimal types, not binary float."),
    "D5": ("Managed determinism",
           "Where reproducibility is required (money/fee calculations, replicable computations, golden tests, output order in API contracts), behavior is explicitly deterministic: randomness — with an injectable seed (in tests), time — an injectable source, collection traversal order — defined, independent of hash randomization; parallelism does not affect the result (or is bounded by explicit merge rules)."),
    "D6": ("Boundary and pathological cases",
           "For every public function/message/schema, boundary cases are enumerated and covered by tests: empty, single, maximum, minimum, zero value, zero items, duplicates, partial partner failure, concurrent access. \"Works on the happy path\" does not count as finished work."),
    "E1": ("Separation of concerns",
           "Merged into **E3** (\"Modularity: separation of concerns and explicit dependencies\") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`. The ID is kept for reference tracing."),
    "E2": ("Minimum necessary abstractions",
           "An abstraction (interface, base class, generalized layer, plugin system) is created only if there is: (a) a second concrete implementation now, or (b) an explicit task requirement. Speculative abstractions \"for the future\" are prohibited. A future customer's requirement is a requirement when it arrives, not when it is presumed."),
    "E3": ("Modularity: separation of concerns and explicit dependencies",
           "Modules have a single stated responsibility and explicit boundaries: domain logic is separated from I/O, frameworks, and transport (formerly E1). All module dependencies are explicit: imports, parameters, injected services; hidden coupling via global mutable variables, implicit \"magic\" configs, and import-time side effects — prohibited. The dependency graph between modules is acyclic within layers, directions are fixed. (Absorbed E1 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)"),
    "E4": ("Minimal public API surface",
           "A module exports the minimum sufficient for its consumers: internal details stay internal; the public API changes by compatibility rules (E7), not by convenience of the moment."),
    "E5": ("External dependency and framework discipline",
           "A new external dependency (library, framework, platform SDK) is added only with a recorded justification: the need it closes, the project's state (alive? tested? secure?), the cost (dependency-tree size, license, attack surface), and the fallback option without it. Versions are pinned by lockfile; the tree is audited."),
    "E6": ("Single source of truth for rules",
           "Business rules, formulas, validations, protocol constants exist in one place. A copy of a rule in a second place is a defect even if it currently matches: divergence is a matter of time."),
    "E7": ("Backward compatibility where consumers exist",
           "Public APIs, data formats, protocols, persistent schemas — are changed with existing consumers in mind: versions, a deprecation period, data migrations. \"Broke the format — update everyone\" is acceptable only if all consumers are in one repository and one deployment."),
    "F1": ("Test pyramid and deterministic tests",
           "Logic is covered by fast unit tests, module interactions — by integration tests, key user scenarios — by a small number of e2e tests. All tests are deterministic: a \"flaky\" test is a defect of the test or the code and must be fixed, not re-run."),
    "F2": ("Static analysis and \"fix the code, not the warning\"",
           "The compiler, linter, type checker, and static analyzer are enabled from day one at maximum strictness; the code builds and analyzes without warnings. Warning suppression — only point-wise, with justification (every suppression is a separate decision, visible in the code). A dubious warning is eliminated by rewriting the code until trivially correct — the NASA requirement verbatim (rule 10: \"even if the analyzer is wrong — rewrite the code that caused the confusion\")."),
    "F3": ("Strict typing where available",
           "In statically typed languages — maximum strict mode; in dynamic ones — where checkers exist (mypy/ty for Python), on modified modules. Bypasses of the type system (`any`, `as unknown`, `unsafe` casts) — only with local justification."),
    "F4": ("Property-based testing",
           "For components with verifiable invariants (parsers/serializers, sorts, aggregations, converters, cryptographic wrappers) — property-based tests: input generation + invariant checking (e.g., round-trip: `decode(encode(x)) == x`; monotonicity; completeness). The test count — a regular run, not a one-off event."),
    "F5": ("Fuzzing of input parsers",
           "Code that parses untrusted data (network protocols, file formats, headers, nested structures) is tested by fuzzing in a regular (nightly) mode with a corpus collector and with sanitizers (for C/C++/Rust — ASan/UBSan mandatory)."),
    "F6": ("Regression as a test",
           "Every fixed defect is accompanied by a test that reproduces it and failed before the fix. \"Fixed it, did not add a test\" — unfinished work. The exception — a defect not expressible as a test — only as an E-C deviation: a record in `EXCEPTIONS.md` (an `EX-…` ID, a verifiably formulated cause — what exactly is not reproducible and why, a compensating control, a review deadline), an anchor in the code, reviewer confirmation. Until the deviation is closed, the defect counts as open."),
    "F7": ("Benchmarks of critical paths",
           "Paths with budgets (B5) are covered by maintainable benchmarks; their results are tracked (C6). A benchmark is code in the repository, not a \"temporary script on a laptop\"."),
    "F8": ("CI gates — the sole enforcer of the standard",
           "All mandatory requirements of the standard that can be checked automatically are checked automatically and block merging. Compliance with the standard is not based on instructions to the agent, team memory, or \"common sense\". The list of gates, modes, and thresholds — in `QUALITY_GATES.md`."),
    "G1": ("Secure defaults",
           "A component in its \"out-of-the-box\" configuration is secure: deny-by-default in access checks, encryption enabled, debug endpoints disabled, verbose errors not exposed, CORS/cookies restricted. Weakening — only by an explicit action with justification."),
    "G2": ("External data is hostile",
           "All external data is treated as hostile: validation at the boundary (D2), safe parsers (no `eval`, no arbitrary deserialization, no query building by concatenation), output escaping by context (HTML/SQL/shell/paths), volume limits (B6)."),
    "G3": ("Dependency security and version hygiene",
           "The dependency tree is audited automatically: known CVEs block the build (or require a registered exception with an applicability assessment), versions are pinned by lockfile, updates are regular. The tree's composition is minimal (E5)."),
    "G4": ("Secrets management",
           "Secrets (passwords, keys, tokens) do not end up in source code, configuration files in the repository, logs, or error messages. Delivery — from a secret store or the deployment's environment variables. Repository scanning — automatic."),
    "G5": ("Least privilege",
           "Every component runs with the minimum necessary rights: an unprivileged container user, scoped tokens, granular DB permissions, minimal cloud roles. A component must not be able to do what its functionality does not require."),
    "G6": ("Fault tolerance and graceful degradation",
           "Interactions with unreliable parties (network, external services, hardware) are designed: timeouts (B6), retries with exponential backoff, jitter, and a hard maximum, idempotent retries, circuit breakers at system boundaries, degradation with partial functionality instead of cascading failure."),
    "H1": ("Task boundaries: do not rewrite unrelated code",
           "Changes are bounded by the task. Incidental improvements (refactoring \"while at it\", renames, reformatting of others' files, updates of unrelated dependencies) — are not done silently: either not done, or split into separate PRs with their own task."),
    "H2": ("No speculative abstractions or architecture expansion beyond the task",
           "The agent does not introduce abstractions, layers, configuration mechanisms, or \"support for future cases\" outside the task requirements. The solution is minimally sufficient for the task. \"It seemed like it might be useful\" is not a reason."),
    "H3": ("No silent changes to public interfaces and contracts",
           "Changing a public API, data format, schema, protocol, or the semantics of existing methods — only deliberately: highlighted in the PR description, assessed for compatibility (E7), approved (if there are external consumers). \"Incidentally changed the signature/behavior\" — prohibited."),
    "H4": ("Do not weaken checks to \"make it green\"",
           "Passing gates by changing the gates themselves is prohibited: disabling/weakening linters and types in config, mass `nolint`/`noqa`/`#[allow]`, lowering test log levels, disabling sanitizers, adding exceptions to CI configuration — in order to pass a check. Suppressing a specific false positive is allowed only point-wise, with a justification comment (see F2, `EXCEPTIONS_POLICY.md`)."),
    "H5": ("Do not bend tests to fit defective code",
           "A test is changed only if it is proven that the test itself is defective (an outdated expectation, an error in the test, changed requirements). Bending expectations to match the actual (defective) behavior of the code — \"made the test green without understanding why\" — is prohibited and counts as a more serious violation than a red test."),
    "H6": ("Do not claim verification you did not perform",
           "Claims of operability (\"tests pass\", \"it builds\", \"checked manually\") are made only based on actually executed commands, with real output. Faking verification (invented output, \"it should work\", skipping a run with the wording \"verified\") — a critical violation, equated to sabotage."),
    "H7": ("No undocumented assumptions about requirements",
           "Ambiguity in requirements is resolved not by a silent choice but by a question (see the stop conditions in `QUALITY_GATES.md`) or — if the task admits a working assumption — by an explicit assumption record marked \"requires confirmation\". Silent interpretation of \"the way I understood it\" — prohibited."),
    "H8": ("Do not change established mathematical, financial, and business rules without explicit permission",
           "Reference values (golden files), calculation formulas, business-rule constants, tax/tariff tables, and compliance rules are not changed within ordinary tasks. Such a change is a separate task with explicit authorization from the rule's owner, an updated specification, and a recorded justification."),
    "H9": ("Diff self-review and honest reporting before submission",
           "Before completing a task the agent must: (1) re-read its full diff as a reviewer; (2) run the gates available in its environment (build, unit tests, lint) — really, with output (H6); (3) verify compliance with task boundaries (H1); (4) in the report, separate facts (what was done and verified) from unconfirmed expectations (what \"should work\" but was not verified)."),
}
