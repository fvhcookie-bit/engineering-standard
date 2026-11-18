# ENGINEERING_PRINCIPLES
## Engineering standard for AI-assisted civilian software development

**Version:** 1.2 · **Status:** active standard (1.2 — track B ROADMAP; version history — `CHANGELOG.md`)
**Basis:** G. J. Holzmann, *The Power of 10: Rules for Developing Safety-Critical Code*, IEEE Computer, vol. 39, no. 6, pp. 95–99, June 2006 (NASA/JPL Laboratory for Reliable Software), DOI: [10.1109/MC.2006.212](https://doi.org/10.1109/MC.2006.212)
**Official translation.** The authoritative text is the Russian original (`standards/ENGINEERING_PRINCIPLES.md`); in case of divergence the Russian wording prevails. Classes: [MANDATORY] = [ОБЯЗ], [RECOMMENDED] = [РЕК], [COND] = [УСЛ]. Line references EP:nnn in `standards/en/DIGEST.md` point into the Russian original.

---

## 0. About this document

### 0.1. Purpose

This standard adapts the ten NASA/JPL "Power of 10" rules, written for safety-critical C code, to modern general-purpose civilian development: desktop, mobile, web and embedded applications, any mainstream languages and frameworks.

The goal is to preserve the **engineering principles** of the original (analyzability, predictability, bounded resources, defensive programming, mechanically checkable enforcement) while rejecting **blind copying** of restrictions that are justified only "where code literally holds lives" (the original's wording).

### 0.2. What the standard optimizes (in priority order)

1. Functional correctness and predictable behavior.
2. Runtime efficiency and frugal resource use.
3. Maintainability and low architectural complexity.
4. Testability and verifiability.
5. Security and fault tolerance.
6. Portability and long-term sustainability.
7. Efficient workflows for AI development agents.

The order matters: correctness over speed, speed over the convenience of optimizations, and all three over code brevity.

### 0.3. What the standard deliberately does NOT do (anti-goals)

- **Does not equate short code with good code.** Mechanically splitting functions to satisfy a formal limit is a violation of the standard, not compliance with it.
- **Does not equate the number of abstractions with architecture quality.** An abstraction without a second concrete consumer is a cost, not an asset.
- **Does not equate green tests with proven correctness.** Tests are a necessary but insufficient signal.
- **Does not assign arbitrary universal limits.** Numeric thresholds (function length, complexity) are *review triggers and signals*, not measures of quality and not stand-alone gates.
- **Does not require optimization without a measurable justification.**
- **Does not rely on agent-prompt instructions alone.** Enforcement is guaranteed by automatic gates (see `QUALITY_GATES.md`), not good will. Some rules are procedural (enforced by review and process artifacts); they are explicitly marked, and their share is published as a maturity metric (see `QUALITY_GATES.md` §6).

### 0.4. How to read

Each principle has:

| Field | Content |
|---|---|
| **Requirement** | brief formulation |
| **Problem** | which defect it prevents |
| **How to comply** | practical guidance |
| **Examples** | ✅ compliant / ❌ non-compliant |
| **Applicability** | project classes where it applies |
| **Automation** | how it is checked mechanically |
| **Exceptions** | allowed deviations and trade-offs |

### 0.5. Requirement classes

| Label | Meaning |
|---|---|
| **[MANDATORY]** | Mandatory (MUST). Deviation — only via `EXCEPTIONS_POLICY.md` |
| **[RECOMMENDED]** | Recommended (SHOULD). Deviation requires a brief justification at review |
| **[COND]** | Conditional (context-dependent). Requires a deliberate decision with the reason recorded |

### 0.6. Project classes (applicability)

| Class | Definition | Examples |
|---|---|---|
| **К1** | Failure- or latency-critical: real time, embedded software, money/health/safety calculations, performance hot spots | drivers, firmware, trading cores, protocols |
| **К2** | General-purpose production: user services, applications, APIs | web services, mobile/desktop applications |
| **К3** | Experimental and internal tools, prototypes, scripts | build scripts, dashboards, MVPs |

The class is fixed in the `REPO_CLASS` file at the repository root (repository class, classes of individual modules, standard version, link to the critical-module manifest). The file is a protected path under CODEOWNERS of the standard's owner (see `QUALITY_GATES.md` §1.5, L0). A class increase takes effect for new changes (existing code moves into the ratchet baseline). A class decrease — only as an E-C deviation with the sign-off "standard's owner", in a separate PR changing only `REPO_CLASS`; reclassification down inside a PR touching code is prohibited (changes to `REPO_CLASS` and code go in different PRs, like the baseline in Q-11 (5)).

The share of К3 code (per Q-19 data) — by default **no more than 20%** of repository lines. The limit is fixed in the project profile; tightening is free, loosening — only via E-D (`gates-change`). Approaching the limit (≥ 16%, i.e. 80% of the default) — an alert to the standard's owner (Q-19); exceeding the limit — red.

### 0.7. Carrier terms

Terms on which blocking gates depend are defined here (duplication in other documents is prohibited):

- **Critical module** — a module from the repository's critical-module manifest (the file referenced by `REPO_CLASS`; changes to the manifest — via `gates-change`).
- **Library** (for the applicability of E4/E7 and gate Q-10) — a repository whose artifact is consumed outside its own deployment cycle (the package type in the build manifest or an explicit declaration in `REPO_CLASS`).
- **Generated code** — files listed in the generation config (paths + generator command). A "generated" mark in the file header does not acknowledge generation; manual edits of generated files are a signal of gate Q-02.
- **Mechanical change** (for gate Q-16) — a change reproducible by a single tool command: formatting, tool-driven rename, regeneration.
- **К3 base gate set** — Q-01 (format), Q-02 (lint, base profile), Q-04 (unit tests), Q-07 (secrets), Q-08 (CVE audit — weekly, non-blocking).
- **Budget path (бюджетный путь)** (for gate Q-13) — a function/module from the list of budget paths: the budgets section of the project documentation (artifact B5), duplicated in the gate Q-13 config. Changes to the list — `gates-change`.
- **Golden reference (golden/snapshot-эталон)** (for gate Q-12) — an oracle file against which code or its output is compared mechanically. The list of golden references is in the Q-12 config (protected path); a new golden reference in the same PR as the code change — enhanced review.
- **Calculation module (расчётный модуль)** (for the semantic signals of Q-12) — a module implementing business formulas, tariffs or financial rules. The list is in the critical-module manifest or in the Q-12 config.
- **Parsing point (точка разбора) of untrusted data** (for gate Q-14) — a function converting external bytes/strings into structures: a parser, a protocol decoder, a format handler. The list of such points (fuzzing targets) is fixed in the repository.
- **Protected path (защищённый путь)** (for L0 — §1.5 `QUALITY_GATES.md`, and guard gates) — a file or directory listed in CODEOWNERS/§1.5.2 or in a guard-gate config: editing requires a CODEOWNERS owner; for gate configs — the `gates-change` label.

Terms **deliberately left to reviewer judgment** (a mechanical definition is impossible; per §5 of `QUALITY_GATES.md` each such rule is formulated as a single checkable checklist question):

| Term | Raised by | Checking question (briefly) |
|---|---|---|
| Real task boundary | H1 / Q-16 | is what is touched actually needed for the task? |
| Speculativeness of an abstraction | E2/H2 / Q-09 | does the abstraction have a second implementation now? |
| Test quality (what exactly it checks) | H5 / Q-04 | does the test check behavior or implementation? |
| Falsity of a specific trigger | Q-11 (part 2) | is the suppression justified by a minimal-code reproduction? |
| Adequacy of the boundary matrix | D6 | does the matrix cover empty/one/maximum/garbage? |
| Sufficiency of verification for the task's risk | H6/H9 / Q-15 | is what can break verified? |
| Validity of a specific exception | EXCEPTIONS_POLICY §4 | are the compensating controls real and in force? |

---

# Domain A. Control flow and program structure

## A1. [MANDATORY] Simple and explicit control flow constructs

**Requirement.** Control is transferred only by explicit, top-down readable structures: sequence, branching, loops, calls, structured error handling. Prohibited: `setjmp`/`longjmp` and their analogues, unstructured jumps, hidden control-flow interception (monkey-patching, remote method substitution); `goto` — outside the centralized resource-cleanup pattern (see below); exceptions — only for exceptional situations, not as a regular control-transfer mechanism.

**Problem.** Unstructured transitions make static analysis of the execution path impossible, produce unreachable branches, hide invariants, and break the locality of reasoning "what happens after this line". This is a direct extension of NASA rule 1: "simple control flow → strong verification capabilities".

**How to comply.**
- Branching — `if/else`, `switch/match` over enumerable values; every `switch/match` over an enumeration must be exhaustive (the compiler requires handling all variants or explicitly setting the default behavior).
- Early return on error — allowed and preferred. NASA explicitly notes: the rule does **not** require a single exit point — "often an early return on error is the simpler solution".
- `goto` in C — legitimate only as the centralized resource-cleanup pattern (one-directional jumps to a common block at the end of the function — established practice, see the Linux kernel coding standard, ch. 7 "Centralized exiting of functions"); no more than one or two per function; never upward or out of the block.
- Exceptions are not used to control the normal flow (validation → return value/Result; "file not found" is not an exception if it is an expected situation).
- Logic with more than two or three interdependent states — an explicit state machine: an enumeration + explicit transitions (switch/match/table), not a cloud of boolean flags (formerly A5); invalid transitions must be impossible by the code's structure.

**Examples.**

```c
/* ✅ C: one-directional cleanup goto */
int read_cfg(cfg_t *out) {
    int rc = ERR;
    FILE *f = fopen(path, "r");
    if (!f) return ERR_OPEN;
    if (parse(f, out) != OK) goto done;
    rc = OK;
done:
    fclose(f);
    return rc;
}
```

```python
# ❌ exception as regular control flow
try:
    value = cache[key]        # KeyError — the normal miss case
except KeyError:
    value = compute(key)
```

**Applicability.** All classes. For К1 — stricter: `goto` exceptions require separate justification at review.

**Automation.** Linters: prohibition of `goto` outside a whitelist of patterns (cppcheck/clang-tidy `goto` rules; eslint `no-constant-condition` etc.), prohibition of `setjmp/longjmp` (grep/clang-tidy), `no-fallthrough`, prohibition of exceptions in "hot" methods (specialized rules). Part is checked statically, part — by review.

**Exceptions.** Interop with C libraries requiring a `setjmp`-like API; legacy code — via `EXCEPTIONS_POLICY.md`. A cleanup-`goto` in the form above is not an exception but the established pattern.

---

## A2. [COND] Bounded recursion

**Requirement.** Recursion is allowed only if the depth is bounded provably (by a data structure with a known maximum depth) or explicitly (a depth parameter + a protective limit). In К1 and in code without a guarantee of bounded input — iteration instead of recursion.

**Problem.** NASA prohibits recursion outright, because without it the call graph is acyclic and stack boundedness is statically checkable. In civilian software the prohibition is too harsh (trees, parsers, `QuickSort`), but the main danger — *stack overflow on unbounded input* — remains real: an attack via "deeply nested" JSON/structure is a classic vulnerability.

**How to comply.**
- Recursion over structures arriving from outside (parsing, traversal) — prohibited without a protective limit: an explicit depth counter with an error on exceeding it.
- The default depth limit is **64**; the value is a named constant next to the recursion, not a "magic number". A project may override it in the profile; for К1 the override is mandatory — based on the stack budget (frame size × limit ≤ stack budget).
- The rule for setting the limit: the limit is set explicitly (constant, config, parameter) and resolved statically; "a limit exists somewhere but is not visible where" — a violation of A2. Absence of both the default and an override — a violation of A2.
- Allowed: recursion over structures with provable height (e.g., a balanced tree: depth O(log n) for bounded n), or with an explicit limit in the signature.
- For "tail" cases — iteration or accumulation into an explicit heap stack with a size cap.
- In К1 — any use of recursion requires a review record stating the depth limit.

**Examples.**

```python
# ❌ recursion on unbounded external input
def walk(node):
    for child in node.children:
        walk(child)               # depth = attack vector
```

```python
# ✅ explicit depth limit
def walk(node, depth=0):
    if depth > MAX_DEPTH:
        raise TreeTooDeep()       # explicitly handled failure
    for child in node.children:
        walk(child, depth + 1)
```

**Applicability.** All classes; in К1 the depth limit is mandatory, in К2/К3 — when working with external data.

**Automation.** Static analysis of call depth (for C — stack-analysis tools); stack sanitizer / tests with pathologically deep inputs; fuzz tests with deeply nested structures.

**Exceptions.** Generators/coroutines, a language with guaranteed tail-call optimization (only if it is documented by the compiler and does not depend on flags).

---

## A3. [MANDATORY] Explicit iteration bounds and runaway-loop protection

**Requirement.** Every loop either has a bound provable from the data structure (array length, collection size) or — if it iterates a potentially unbounded or external source — must have an explicit protective iteration limit (guard) and defined behavior when it is exceeded. Loops intended to be infinite (event loops, schedulers, servers) are allowed, but must demonstrate a progress guarantee or a timeout on every iteration.

**Problem.** NASA rule 2: "all loops must have a fixed upper bound… if the bound cannot be proven statically, the rule is violated". The goal is to eliminate "runaway" code: infinite/quasi-infinite loops on external input, hangs, starvation. NASA itself notes the exception for "iterations intended to be non-interruptible".

**How to comply.**
- A loop over a collection — by its size; in languages with `while` semantics (stream reading) — an explicit maximum of iterations/bytes.
- Waiting for a condition (polling, retry) — with a timeout and a maximum number of attempts, not "until it works".
- Reading from network/file — with a volume limit (see B6), so that "unbounded input" does not turn a bounded loop into an infinite one.
- Event loops: every iteration has a deadline or a hang-detection mechanism (watchdog).

**Examples.**

```c
/* ✅ explicit limit when reading external data */
size_t total = 0;
while ((n = read(fd, buf, sizeof buf)) > 0) {
    if ((total += n) > MAX_UPLOAD) return ERR_TOO_LARGE;
}
```

```
❌ while (!queue.try_pop(item));        // busy-wait without a timeout
✅ item = queue.pop_with_timeout(deadline) or fail(TIMEOUT)
```

**Applicability.** All classes. In К1 statically provable boundedness (WCET analysis) is mandatory.

**Automation.** Static loop analysis (flow analysis, bounded-loop checks in strict modes); timeout tests in CI (a test not finishing within N seconds fails); sanitizer/hang detectors in the nightly run.

**Exceptions.** Hard real-time polling with a correct OS-level timeout configuration; documented exceptions per policy.

---

## A4. [RECOMMENDED] Function and module complexity control — triggers, not dogmas

**Requirement.** Numeric complexity thresholds (function length, cyclomatic complexity, parameter count) are used as **triggers for mandatory explanation at review**, not as automatic gates and not as a measure of quality. Exceeding a threshold requires one or two sentences from the author on "why this is better", not mechanical splitting.

**Problem.** NASA (rule 4): "a function should not be longer than what fits on one sheet of paper… usually about 60 lines", because a function is a logical unit understood and checked as a whole. The danger of the adaptation: turning "60 lines" into a hard gate produces either counter games (splitting for the sake of lines) or meaningless wrappers. The opposite danger: thousands of lines in one function is a real sign of bad structure.

**How to comply.**
- Starting trigger thresholds (tuned per project): function length > 60–80 lines; cyclomatic complexity > 10–15; > 4–5 parameters; branching nesting > 3–4.
- Threshold crossed → the PR requires a justification OR a refactoring. A justification is a legitimate outcome.
- A long function with a linear, homogeneous flow (a data table, a large `match`) can be shorter than an equivalent chain of wrappers — this is **allowed and sometimes better**.
- A module requiring N screens of scrolling to understand one rule — a signal to split; a module of 100 homogeneous declarations — a signal to generate data, not to "abstract".

**Examples.**

```
❌ Mechanical splitting for the sake of the limit:
   process_order() → _step1() → _step2() → ... → _step9()
   (called in order from a single wrapper function; the limit is "met", comprehensibility — no)
✅ One 120-line function consisting of a flat configuration table,
   with a review justification: "a data table, not split without losing context".
```

**Applicability.** All classes as a trigger. As an automatic blocking gate — nowhere.

**Automation.** A two-level scheme (gate Q-02): (a) absolute thresholds — warning + a comment in the PR, never blocking by themselves; (b) a ratchet on changed functions — blocking: a function *modified* in a PR cannot exceed the threshold without an explicit justification checkbox in the PR template (presence is checked mechanically, quality — by review). Silently introducing a 500-line function becomes impossible, while "explain why this is better" remains a legitimate outcome.

**Exceptions.** Generated code is excluded from the count. Thresholds are a matter of project tuning, not universal truth.

---

## A5. [merged into A1] Explicit state transitions

Merged into **A1** ("Simple and explicit control flow constructs") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: explicit state machines moved into the survivor's "How to comply" section. The ID is kept for reference tracing.

---

## A6. [MANDATORY] Minimal scope and minimal shared mutable state

**Requirement.** Data is declared in the smallest sufficient scope. New mutable global variables, publicly mutable module fields, and mutable singletons are prohibited without explicit justification. Preference — immutable data.

**Problem.** NASA rule 6 (preserved verbatim): "an object outside the scope cannot be read or corrupted"; the fewer places a variable is assigned, the easier defects are to diagnose. Wide visibility + mutability = hidden coupling: any place in the program can break any other, and the gap in time ("who corrupted the state?") is not localizable.

**How to comply.**
- Declare a variable at the moment of its first meaningful assignment, in the innermost block.
- A function reads data via parameters, not via external mutable variables.
- Constants and configuration — immutable (`const`, `final`, private with getters).
- A module's public mutable status — replaced by methods with defined semantics ("encapsulation of an invariant", not "an open field").

**Examples.**

```go
// ❌
var result []Row   // package-level result variable, visible to all
func f() { result = query() }

// ✅
func f() []Row { return query() }   // data via the call flow
```

**Applicability.** All classes.

**Automation.** Linters: prohibition of package-level `var` outside an allow-list (Go `unused`/review; ESLint `no-var` — partially), "exported mutable" checks, static analysis of global assignments (clang-tidy `misc-non-private-member-variables-in-classes`, the rule about global mutables).

**Exceptions.** Truly global immutable constants; legacy globals — only fixing in the baseline and prohibiting growth.

---

## A7. [RECOMMENDED] Conditional compilation and feature-flag discipline

**Requirement.** The combinatorics of build and behavior variants is controlled explicitly: conditional compilation (`#ifdef`, build tags, build configs) is minimal, every variant is included in the CI matrix; feature flags have an owner, a removal deadline, and a test of both branches; "eternal" flags and flags without a test of the disabled branch are a defect.

**Problem.** A direct extension of NASA rule 8: "10 conditional directives — up to 2¹⁰ code variants, each of which must be tested". Modern forms of the same combinatorics — build tags, config flags, platform branches; unmanaged, they yield untested variants in production and dead code.

**How to comply.**
- Every conditional compilation — with a reason comment; the variant is included in the CI matrix (for К1 — building all combinations is mandatory).
- A feature flag: owner, removal date, removal ticket; both branches covered by tests (the disabled branch too).
- Environment configuration is not a way to branch logic; logic branches on explicit data, not on "where it is deployed".

**Examples.**

```rust
// ❌ a variant outside the CI matrix: builds locally, never enters the pipeline
#[cfg(target_os = "qnx")]
fn fast_path() { ... }

// ✅ a variant in the build matrix + a reason comment
// build-matrix: the qnx build is part of the nightly matrix
#[cfg(target_os = "qnx")]
fn fast_path() { ... }
```

**Applicability.** [RECOMMENDED] everywhere; for К1 — [MANDATORY] (CI matrix of variants).

**Automation.** Counting conditional directives against a baseline (Q-02), matrix builds in CI (Q-01/Q-04), feature-flag accounting — per project.

**Exceptions.** Experimental К3 code — marked "not for production".

---

# Domain B. Memory and resource management

## B1. [MANDATORY] Predictable and bounded memory consumption

**Requirement.** The memory-allocation strategy is determined by the system class and fixed explicitly. К1 (real-time/embedded): allocation only at initialization time or from pre-allocated pools; after initialization — no allocations (NASA rule 3 is preserved verbatim). К2: allocation is allowed but bounded — volumes are limited, collection growth has a cap, behavior under maximum load is predictable and verified. Memory and handle leaks are absent; copying large data unnecessarily without measurement is not allowed. (Absorbed B2 and B4 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)

**Problem.** NASA rule 3: allocators and garbage collectors have unpredictable behavior; a class of errors (leaks, use-after-free, buffer overruns, requesting more than available) is excluded by working within pre-allocated memory. In GC languages prohibiting allocations is impossible — the requirement shifts to *boundedness and predictability*: unpredictable memory manifests as latency degradation, OOM kills, "sudden" degradation under load; a leak is the classic failure of long-lived systems.

**How to comply.**
- Fix the strategy in the module: "allocations only at startup", "a fixed-size pool", "unbounded but with a volume cap" — and follow it.
- All containers growing from external input or over time have an upper limit / eviction.
- In К1: a stack without recursion (A2) yields a statically derivable upper memory estimate — preserve this property.
- GC languages: do not hold references longer than necessary; avoid unbounded caches; large buffers — reusable.
- Leaks (formerly B4): CI — AddressSanitizer/LeakSanitizer (C/C++), load runs without monotonic RSS growth and with heap-dump analysis when suspected (JVM); early exit on error still releases resources (B3).
- Copying (formerly B2): for small short-lived objects — clarity over micro-optimizations; for large structures and hot paths — move, borrow, mutate in place; ownership transfer — explicit (`unique_ptr`, wrapper types), not "by agreement".

**Examples.**

```c
/* ✅ К1: all memory from a pool allocated at startup */
static entity_t pool[MAX_ENTITIES];
entity_t *spawn(void) { ... from a free slot ... }
```

```python
# ❌ К2: unbounded growth from external input
sessions[key] = Session(...)      # no cap on the number of sessions
# ✅
if len(sessions) >= MAX_SESSIONS: evict_oldest()
```

**Applicability.** All classes; the formulation differs by class (see the requirement).

**Automation.** К1: static stack/heap analysis tools prohibiting `malloc` outside init; К2: memory and leak tests (sanitizers, load runs with RSS monitoring), allocation profiles in nightly runs.

**Exceptions.** К2 systems where predictability is proven otherwise (orchestration with memory limits, autoscaling) — fixed in project documentation, not as a silent assumption. Defensive copies at public API boundaries (invariant protection) — a deliberate cost, not an error (formerly B2). "Pinned" structures (metadata caches) — expected growth with a fixed cap (formerly B4).

---

## B2. [merged into B1] Frugal data creation and copying

Merged into **B1** ("Predictable and bounded memory consumption") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`. Content moved into the survivor's "How to comply" and "Exceptions" sections. The ID is kept for reference tracing.

---

## B3. [MANDATORY] Deterministic resource lifetime management

**Requirement.** The lifetime of every resource (files, sockets, connections, locks, transactions, subscriptions) is managed by a language mechanism of deterministic release: RAII / `using` / `try-with-resources` / `defer` / context manager. Manual release "in the right place" is prohibited as an approach.

**Problem.** Manual `open…close`/`acquire…release` with error branches reliably leads to leaks on early exits and to hangs while holding a lock. NASA rule 3 eliminated this by eliminating the manual work itself; in GC languages "a finalizer sometime later" is not a release.

**How to comply.**
- A resource is opened in a scope's constructor and released at its end — by the language's automatic mechanism.
- Release must happen even on error (stack unwinding, panic-unwind) — the language mechanism is chosen so that this is guaranteed.
- Do not "reassign" handles before closing the old one.
- Order: acquire → use → release; for several resources — nested/sequential scopes without overlap, unless the order is set by a protocol.

**Examples.**

```java
// ❌
Connection c = pool.get();
runQuery(c);              // on exception the connection leaked
c.close();

// ✅
try (Connection c = pool.get()) { runQuery(c); }
```

```go
// ✅
mu.Lock(); defer mu.Unlock()
```

**Applicability.** All classes, all languages.

**Automation.** Linters: `golangci-lint` (defer in a loop — warning), pylint for unclosed handles, clang static analyzer (leak checker), `reraise` checks; sanitizers on CI; tests "an exception inside a scope → the resource is closed".

**Exceptions.** Resources with intentionally long lifetimes (pools, caches) — managed by an explicit owner with a clear lifecycle; this is not an exception from RAII but its organized form.

---

## B4. [merged into B1] Leak control

Merged into **B1** ("Predictable and bounded memory consumption") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`. Content (sanitizers on CI, memory stability under load, eviction of growing structures) moved into the survivor's "How to comply" and "Automation" sections. The ID is kept for reference tracing.

---

## B5. [RECOMMENDED] CPU/RAM/disk/network efficiency — by budget, not intuition

**Requirement.** For components whose resource consumption is a product property (request latency, on-device memory, mobile-app traffic), explicit budgets are defined; code is checked against budgets, not feelings. For components without such properties — "fast enough" and the no-premature-optimization rule (C4).

**Problem.** Without budgets "efficiency" degenerates into local micro-optimizations for their own sake or, conversely, into ignoring systemic degradation. With budgets the argument becomes a measurement.

**How to comply.**
- A budget is a "scenario → number" pair (e.g., "message processing ≤ 5 ms p99 on reference hardware").
- Code consuming a budget — checked by a benchmark; exceeding it is a defect, not a matter of taste.
- Network calls — not in a loop over N if N grows with data (N+1 queries — a typical defect).

**Applicability.** [COND]: exists if a budget is defined. Defining budgets is the component owner's duty at the start; the artifact — the budgets section in the component's project documentation (owner + revision date). The absence of a budget where efficiency is declared a product property — a question to the component owner at planning time.

**Automation.** Benchmarks with thresholds (C6/F7); profiling in CI on signal.

**Exceptions.** — (the requirement is null when there is no budget).

---

## B6. [MANDATORY] Explicit resource limits on every external interaction

**Requirement.** Every interaction with the outside world (network, files, user input, inter-process communication) has explicit limits: a timeout, a maximum size, a maximum number of items/attempts — and defined behavior on exceeding them (error, request rejection, degradation). "Wait as long as it takes" and "accept as much as comes" are prohibited.

**Problem.** This is a direct extension of NASA rule 2 toward modern architecture: unbounded external input turns any loop into an infinite one (A3), any queue — into an overflow, any timeout — into a hang. Limitation is a cheap form of fault tolerance: a system with limits degrades predictably; without them — unpredictably.

**How to comply.**
- A timeout on every network call (connect, read, write), DB query, lock wait.
- Size limits: request body, file, structure depth, string length.
- Bounded queues/pools: instead of unbounded collections "just in case".
- Behavior on exceeding the limits — defined and covered by a test: a rejection with a clear error code, not a silent "hang".

Default limits (the project profile overrides them; inheriting a value from config/context is allowed only if it resolves statically and is stated in a comment at the call site):

| Interaction | Timeout | Other limits |
|---|---|---|
| Network: connect | ≤ 5 s | — |
| Network: read/write (idle) | ≤ 30 s | retries ≤ 3, backoff with a ceiling ≤ 60 s |
| Network: total request budget | ≤ 60 s | streaming — a separate explicit budget |
| DB query (OLTP) | ≤ 5 s | analytics/batch — a budget at the call site with justification |
| Queue: waiting for a message | ≤ 30 s | the queue is size-bounded |
| File I/O: operation | ≤ 10 s | or a justification in a comment |

A size limit (request body, file, structure depth, string length) — an explicit constant; there is no universal default, "accept as much as comes" is prohibited (see the Requirement above).

**Examples.**

```py
# ❌
resp = requests.get(url)                    # no timeout
# ✅
resp = requests.get(url, timeout=(3, 10), stream=True,
                    allow_redirects=3)      # plus a size check when streaming
```

**Applicability.** All classes. In К1 — additionally static WCET analysis where applicable.

**Automation.** Linters (requests without a timeout — detectors), tests on "pathological input" (see D6), load tests with bounded input; review checks per the checklist "every I/O call: timeout? limit? behavior on exceeding?".

**Exceptions.** Inter-process communication with a guaranteed instantaneous operation (shared memory, lock-free) — with justification.

---

# Domain C. Algorithms and performance

## C1. [RECOMMENDED] Deliberate complexity: algorithms, recomputation, data structures

**Requirement.** For operations over collections whose size grows with external data, complexity must be deliberate: the author understands and, when needed, documents it (e.g., "O(n·m) is acceptable, m≤8"). Accidental quadratic behavior on a user-controlled path is a defect. Loop-invariant computations are moved out of the loop; caching — only with a measured need and an eviction policy. The data structure is chosen by the dominant access pattern, not by habit. (Absorbed C2 and C3 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)

**Problem.** The most expensive category of production performance incidents is not "a slow algorithm" but "the right algorithm in the wrong context": sorting inside a loop, searching a list instead of a set, string concatenation in a loop. Next to it — recomputation (N+1 queries, recomputing an aggregate on every render) and cache as a bug source: stale data, unbounded growth (see B1), divergence from the source. The same logic on an unlucky structure is a frequent cause of both quadratic behavior and leaks.

**How to comply.**
- For every place where "external N" meets "internal M", ask: what happens at N=10⁶?
- The standard library by default (its implementations are usually correct and efficient); own algorithms and own structures — only with a reason.
- When choosing "worse in complexity but simpler" — an acceptable decision, recorded in one comment line ("here n ≤ 100 by the API contract").
- Recomputation (formerly C2): hoist invariants; memoization — with a key, a TTL/invalidation policy, an upper size bound, and defined behavior on a miss; do not cache where the computation cost is comparable to the cache cost.
- Data structures (formerly C3): frequent lookup by key → hash table; ordered traversal → tree/sorted list; FIFO → a bounded queue; uniqueness → a set. The right structure often simplifies the code: a set replaces a nested loop with a check.

**Examples.**

```ts
// ❌ quadratic behavior on user data
for (const id of incoming) { if (processed.find(p => p.id === id)) ... }

// ✅
const seen = new Set(processed.map(p => p.id));
for (const id of incoming) { if (seen.has(id)) ... }
```

**Applicability.** [RECOMMENDED] everywhere; [MANDATORY] for modules with a budget (B5).

**Automation.** Static detectors of "a loop with a search in a list inside", "list.contains in a loop" (partially), micro-benchmark profiles in nightly runs; tests "a repeated call returns a consistent value" for caches with invalidation; mostly — review and tests at large volumes.

**Exceptions.** Small guaranteed N ("≤ 8 items") — O(n²) is acceptable if N is genuinely guaranteed by the structure. Structures with useful side properties (dictionary ordering) — acceptable if the dependency is documented. Absence of performance measurements — a question to C4/C5, not a deviation of C1.

---

## C2. [merged into C1] Do not repeat computations needlessly

Merged into **C1** ("Deliberate complexity") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: loop-invariant extraction and memoization/cache discipline moved into the survivor's "How to comply" section. The ID is kept for reference tracing.

---

## C3. [merged into C1] Appropriate data structures

Merged into **C1** ("Deliberate complexity") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: data-structure selection by access pattern moved into the survivor's "How to comply" section. The ID is kept for reference tracing.

---

## C4. [RECOMMENDED] No premature optimization

**Requirement.** No optimization without a problem: a measured degradation, an unmet budget, or a demonstrable asymptotic error (C1). Readability and simplicity are the default behavior. "Optimizing just in case" is a violation of the standard.

**Problem.** Premature optimization is a source of complexity, defects, and unmaintainability; most "optimizations" without measurement do not improve what matters (Holzmann in the original silently assumes the same: the rules target *verifiability*, not micro-efficiency). A double error: complicate the code and fail to speed up the system.

**How to comply.**
- Write simply and clearly; optimize what is measured as a problem.
- "Obviously expensive" places (parsing, serialization, O(N²)) — design them sensibly right away (this is C1, not premature optimization).
- A performance patch comes with "before/after" measurements in the PR.

**Applicability.** All classes.

**Automation.** Review: changing a hot path without measurement — a question to the reviewer. Mechanically — not fully; this is a cultural rule with partial control through C5.

**Exceptions.** None. "Justified foresight" is C1.

---

## C5. [RECOMMENDED] Profile before optimizing

**Requirement.** Substantial performance work starts with a profile on representative load. A PR with optimization contains "before/after" measurements (numbers, scenario, hardware/configuration). A patch that did not show an improvement under measurement is not accepted as an optimization.

**Problem.** Intuition about "hot spots" is systematically wrong (a well-known empirical result: the actual time distribution is power-law, and developers predict it poorly). A profile before is the only way to make sure what is being optimized matters at all.

**How to comply.**
- Profile on realistic data (not on "three records from a test database").
- Measure by user-facing metrics (p50/p99 latency), not averages.
- After the patch — re-measure the same way; the result in the PR description.

**Applicability.** [MANDATORY] for work declared as optimizations.

**Automation.** Partial: benchmark tracking in CI (C6) gives "before"; "after" is checked by the PR benchmark. The cultural part — review.

**Exceptions.** Micro-optimizations in an already-profiled and admittedly hot place (e.g., an inner loop noticed in a profile) — then the profile already exists, the rule is fulfilled.

---

## C6. [COND] Performance-regression protection

**Requirement.** For components with budgets (B5), automated benchmarks exist on critical paths, run regularly (at minimum — nightly), with alerts on threshold breaches. An alert is a signal to investigate, not to immediately "make it faster": first a profile (C5), then a decision (optimize / revise the budget / roll back).

**Problem.** Without tracking, performance degrades "drop by drop": each individual MR is imperceptible, the sum over a year is an incident. A regression found by an alert a week after the MR is localizable; one found by a user a year later — is not.

**How to comply.**
- Benchmarks — only for paths with a budget (otherwise noise and false triggers).
- Alert threshold: e.g., > +20% p99 on a reference run in a stable environment; sensitivity is tuned so that false alerts are few.
- Noise isolation: fixed hardware/environment, repeated runs, outlier rejection.

**Applicability.** [COND]: mandatory when there is a budget; redundant when there is none.

**Automation.** A nightly job recording metrics into a time-series store; an automatic comparative report in the PR when budget paths change (see `QUALITY_GATES.md`).

**Exceptions.** — (the rule does not apply without budgets).

---

# Domain D. Reliability and correctness

## D1. [RECOMMENDED] Explicit contracts: preconditions, postconditions, invariants

**Requirement.** Every non-trivial function has expressed contracts: preconditions and postconditions — via types (impossibility of an invalid value), assert checks, or brief documentation; structure invariants are concentrated in one place (methods of the type), not smeared across callers. Assert checks are free of side effects, boolean, with an explicit action on failure; meaningless checks (`assert(true)`, always-true conditions) are prohibited (at NASA — a direct requirement of rule 5).

**Problem.** NASA rule 5 introduced the quota "on average ≥ 2 asserts per function" for C — a language where contracts have nowhere else to be expressed. The goal: to increase the density of early defect detection (statistics in the original: unit tests find ≥ 1 defect per 10–100 lines). In modern languages a significant share of contracts moves into the type system (`Option` instead of null, `Result` instead of error codes, non-empty strings, ranges) — better than assert: checked by the compiler. The remainder (values from the outside world, invariants of composite structures) — assert/validation.

**How to comply.**
- Types first: make an invalid state inexpressible. If a parameter cannot be empty — a "non-empty string" type, not an assert on an empty string.
- What is not expressible by a type — assert in debug builds + explicit handling in production (return an error rather than "crash" at runtime where the failure is expected).
- An assert must have no side effects; it does not change program behavior except for the failure branch (the NASA requirement preserved verbatim).
- An invariant (e.g., "the sum of positions == the sum of payments") is checked by one method of the type, not at every call.

**Examples.**

```rust
// ✅ contract in the type: an invalid value is inexpressible
fn withdraw(acc: &mut Account, amount: Cents) -> Result<(), Overdraft>
// Cents — an opaque type, cannot be negative

// ❌ contract in a comment + silent behavior
// amount must be positive!!!
fn withdraw(acc: &mut Account, amount: f64) { acc.balance -= amount; }
```

**Applicability.** [RECOMMENDED] everywhere; for К1 — [MANDATORY]: presence and meaningfulness of checks for every public function (control density as at NASA, without the literal "2 per function" quota).

**Automation.** Strict type modes; linters for empty/constant asserts; static verifiers where mature (SPARK/Ada, Frama-C — for К1 by choice); review: "is the contract visible in the signature?"

**Exceptions.** The "2 asserts per function" quota from the original is not reproduced as a universal norm: applying it is justified in К1 C code; in typed languages it would be a bad incentive (assert stuffing). Dropping the quota — a deliberate adaptation, not an omission.

---

## D2. [MANDATORY] Input validation and explicit error handling

**Requirement.** Every input from the outside world (user input, network, files, broker messages, environment variables, CLI arguments, data from other services) is validated at system entry: schema/type/range/size — and either accepted in full or rejected with an explicit error. Inside the system after validation — trusted types. Errors are not silently ignored: every failure is handled meaningfully, logged with context, and propagated upward, or explicitly ignored via intentional-ignore syntax. (Absorbed D3 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)

**Problem.** NASA rule 7 (parameter checking) in modern systems is localized at boundaries: that is where hostile and simply unforeseen data arrives; deeper in the stack, already-checked types flow. A missed boundary = the entire content of bugs and vulnerabilities (see G2): injections, overflows, logical holes. Checking "in every place just in case" — the opposite extreme: duplication and a false sense of security.

**How to comply.**
- One validation point per boundary (deserialization into a strictly typed structure with checks).
- A validation error — explicit and uniform (error code, field, reason); no "default to 0 and move on".
- "Boundary" is defined architecturally: an API controller, a message parser, a config loader.
- Internal calls between trusted modules — without re-validation (D1 contracts), except where a function is public with respect to foreign data.
- An error is classified (formerly D3): expected — a meaningful result; an invariant defect — fail fast with diagnostics. Every `catch` has content: handle, log+propagate, wrap with context.
- Explicit ignoring of returns/errors — only via intentional-ignore syntax (`_`, `(void)f()`, `#[allow]` with a comment "why the ignore is safe") — a technique named explicitly at NASA.

**Examples.**

```ts
// ✅ boundary: a string from the network → a validated domain type
const req = parseRequest(raw);       // Schema.parse: fails with a field code
// further in the code: req.amount — a validated type, no checks needed
```

```python
# ❌ validation "deep inside"
def transfer(acc, amount):
    if amount < 0: raise ...   # and at the API input? and from the broker?
```

**Applicability.** [MANDATORY] all classes.

**Automation.** Schemas/validators (JSON Schema, pydantic, zod, protobuf), boundary tests on garbage input, fuzz (F5); linters for "deserialization without a validator" (partially); linters for "do not swallow errors" (formerly D3): `errcheck` (Go), `no-empty-catch`, `#[must_use]`/ErrorProne, `no-floating-promises` (TS) — one of the most mechanically checkable rules.

**Exceptions.** Internal calls between trusted modules — per the D1 contract; this is not "the absence of validation" but its relocation into types. Justified `(void)` ignores — legitimate at NASA, legitimate here; each — with a comment "why the ignore is safe".

---

## D3. [merged into D2] Complete and explicit error handling

Merged into **D2** ("Input validation and explicit error handling") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`: error classification, `catch` discipline, and intentional-ignore syntax moved into the survivor's "How to comply" section (NASA r.7). The ID is kept for reference tracing.

---

## D4. [COND] Numerical correctness

**Requirement.** Numeric computations are performed correctly: floating-point comparison with a tolerance, operation order accounts for error accumulation, integer operations with overflow control where it is possible (external data, size arithmetic), NaN/Infinity do not propagate "quietly". For money — integer minor units or decimal types, not binary float.

**Problem.** Floating-point arithmetic is non-associative and approximate: `0.1+0.2 != 0.3`; error accumulation in a loop gives "drift"; integer overflow is a well-known vulnerability class (this supplements the NASA rules beyond rule 7 — data-correctness checking). Numeric defects are insidious: they work on test data and break in production.

**How to comply.**
- `a == b` for floats — only via `abs(a-b) <= eps` with a meaningful eps per context (or ULP comparison in numerical kernels).
- Summing long sequences — compensated/Kahan summation or a higher-precision accumulator under an accuracy budget.
- Overflow: languages with checkable overflow — enable checks (debug — crash, release — saturating/panic per project choice); in C — explicit checks before the operation.
- Financial values — `int64` minor units or decimal; float for money — prohibited.

**Examples.**

```py
# ❌
total = sum(order.lines)          # float kopecks
if price == 0.1 + 0.2: ...

# ✅
total = sum(line.minor_units for line in order.lines)   # int kopecks
if abs(x - y) <= EPS: ...
```

**Applicability.** [COND]: applies where there is non-trivial numerics (finance, graphics, physics, statistics). Does not require CRUD code to have measurements it does not have.

**Automation.** Linters for "float in money" (partially), property-based tests with invariants (F4), overflow sanitizers (UBSan in C/C++), integer checks in Rust debug by default.

**Exceptions.** Games/graphics: a tolerance for approximation can be part of the specification — then it is a specification, not a defect.

---

## D5. [COND] Managed determinism

**Requirement.** Where reproducibility is required (money/fee calculations, replicable computations, golden tests, output order in API contracts), behavior is explicitly deterministic: randomness — with an injectable seed (in tests), time — an injectable source, collection traversal order — defined, independent of hash randomization; parallelism does not affect the result (or is bounded by explicit merge rules).

**Problem.** Non-determinism is the main cause of "flaky" tests and non-reproducible incidents: the same code on test and production gives different results, and the bug cannot be reproduced. The NASA context did not require this explicitly, but the "predictable behavior" principle is central.

**How to comply.**
- `Random`/`now()` — via injectable dependencies in the logic; at the boundaries — the real ones.
- Fix the traversal order of hash collections affecting output/serialization (sorting keys).
- Iterations over parallel data with accumulation — only with an associative operation or a fixed merge order.
- Tests — deterministic; the randomness seed in tests is fixed (or reported on failure).

**Applicability.** [COND]: applies to financial/replicable/contractual logic and tests; does not require determinism from systems that do not need it (recommendations, animations).

**Automation.** Tests with a fixed seed by default; property-based tests with a reproducible seed in the failure report; linters for "Math.random in business logic" (partially).

**Exceptions.** Explicitly non-deterministic components (recommendation generators) — marked as such; their tests check distribution properties, not equality.

---

## D6. [RECOMMENDED] Boundary and pathological cases

**Requirement.** For every public function/message/schema, boundary cases are enumerated and covered by tests: empty, single, maximum, minimum, zero value, zero items, duplicates, partial partner failure, concurrent access. "Works on the happy path" does not count as finished work.

**Problem.** Defects concentrate at boundaries (an empirically known fact, confirmed also by NASA's unit-testing practice: "tests find ≥ 1 defect per 10–100 lines"). A function whose boundary behavior is undefined is an unfinished specification.

**How to comply.**
- The boundary matrix is written before the code (or simultaneously): inputs → outputs for: empty / one / two / maximum / maximum+1 / garbage / duplicate / partially corrupted.
- For sequences and aggregates: what will the function return on empty input? (an error — the most frequent "undefined").
- For external partners: timeout, partial response, retry-duplicate (idempotency).
- The boundary table — in tests, not in "verbal" documentation.

**Applicability.** [RECOMMENDED] everywhere; for public APIs of К1/К2 — de facto mandatory via review and partial mechanical analogues (property/fuzz); there is no direct gate on matrix completeness — a recognized limitation.

**Automation.** Partial: property-based tests explore the input space and find unstated boundaries (they do not guarantee matrix completeness); parameterized tests from the matrix; fuzz for parsing points of external data. Boundary-matrix completeness is checked by review.

**Exceptions.** К3 prototypes: the "maximum+1" boundary may be postponed — with a deliberate "not for production" record.

---

# Domain E. Architecture and maintainability

## E1. [merged into E3] Separation of concerns

Merged into **E3** ("Modularity: separation of concerns and explicit dependencies") — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`. The ID is kept for reference tracing.

---

## E2. [MANDATORY] Minimum necessary abstractions

**Requirement.** An abstraction (interface, base class, generalized layer, plugin system) is created only if there is: (a) a second concrete implementation now, or (b) an explicit task requirement. Speculative abstractions "for the future" are prohibited. A future customer's requirement is a requirement when it arrives, not when it is presumed.

**Problem.** An extra level of indirection multiplies code and comprehension time without adding capability; "future extensibility" almost always guesses the future wrong and is rewritten. This is a direct anti-pattern for AI agents prone to "improving" architecture beyond the task (see H2).

**How to comply.**
- The "two implementations" rule: build concretely; when a second implementation appears — introduce an interface, extracting it from facts, not fantasies.
- An interface with a single implementation and a single consumer — a red flag (except where it solves a concrete technical problem: a test substitution of a heavy dependency is also a concrete second, test, implementation).
- Removing an abstraction — as normal a refactoring as adding one.

**Examples.**

```
❌ Repository<T> with one implementation SqlRepository<T> and one CRUD controller
✅ Direct DB calls in the service; an interface will appear with a second implementation/test substitution
```

**Applicability.** [MANDATORY] all classes (the cheapest rule to comply with: "do nothing").

**Automation.** The metric "an interface with 1 implementation and no test substitution" — a review signal (computed automatically partially); mostly — the review checklist.

**Exceptions.** Integration points with external heavy systems (DBs, gateways), where a test substitution is a need now, not "for the future".

---

## E3. [MANDATORY] Modularity: separation of concerns and explicit dependencies

**Requirement.** Modules have a single stated responsibility and explicit boundaries: domain logic is separated from I/O, frameworks, and transport (formerly E1). All module dependencies are explicit: imports, parameters, injected services; hidden coupling via global mutable variables, implicit "magic" configs, and import-time side effects — prohibited. The dependency graph between modules is acyclic within layers, directions are fixed. (Absorbed E1 — owner decision 2026-11-16, map `standards/review/REDUCTION_MAP_v1.2.md`.)

**Problem.** Mixing logic with transport/framework makes the logic untestable without infrastructure and makes a framework change a system rewrite. NASA rule 9 restricted pointers so the data flow was traceable by analyzers; the modern analogue — dependency traceability: if "everything depends on everything", changing any module can break any other, and no tool can say which one. Hidden import-time side effects make program behavior depend on load order.

**How to comply.**
- Every module — one stated responsibility (one sentence); if there are five sentences, that is five modules (or one tangled one).
- No actions at module import/initialization other than definitions.
- Dependencies — via parameters/constructor; global mutable services — only as a justified exception (see A6).
- Fix and check: "the domain does not depend on transport", "shared code does not depend on the domain", etc. per project.
- Cyclic module dependencies — eliminated by extracting a common lower level.
- Do not design "for the future" more layers than needed now (see E2): the typical minimum for К2 — domain / application / adapters, without "six layers of clean architecture" in a CRUD app.

**Automation.** dependency-cruiser / import-linter / ArchUnit / jdeps — blocking gates on import directions and cycles; prohibition of "domain → framework".

**Applicability.** [MANDATORY] all classes (for К3 — minimum: no cycles).

**Exceptions.** Plugin systems — a "cycle" through an explicitly described registration point (a registry); this is not hidden coupling but an explicit mechanism. Small utilities/scripts (К3) — a single module is acceptable.

---

## E4. [RECOMMENDED] Minimal public API surface

**Requirement.** A module exports the minimum sufficient for its consumers: internal details stay internal; the public API changes by compatibility rules (E7), not by convenience of the moment.

**Problem.** Every public entity is a maintenance obligation and a coupling source (someone may already have started using it). A wide surface = slow evolution and fear of refactoring.

**How to comply.**
- Export types/functions, not structure fields; provide methods with invariants instead of "bare" collections.
- "Temporarily public for tests" — do not publish: tests have access to internals (a test package/module, `#[cfg(test)]`, internal packages).
- New public API in a PR — separately marked in the description, passes a compatibility check.

**Applicability.** [RECOMMENDED] everywhere; for libraries (definition — §0.7) and К1/К2 platforms — practically [MANDATORY] (a versioning policy).

**Automation.** API-diff in CI (api-diff/rustdoc-json/gitdiff export checks), review.

**Exceptions.** Internal monoliths: "public" within a single product — a soft policy.

---

## E5. [MANDATORY] External dependency and framework discipline

**Requirement.** A new external dependency (library, framework, platform SDK) is added only with a recorded justification: the need it closes, the project's state (alive? tested? secure?), the cost (dependency-tree size, license, attack surface), and the fallback option without it. Versions are pinned by lockfile; the tree is audited.

**Problem.** NASA rule 8 restricted the preprocessor as a "powerful obfuscation tool" that multiplies checkable code versions (10 conditional directives → up to 2¹⁰ variants). The modern analogue of state multiplication — the dependency tree: every library is someone else's code with its own versions, defects, and CVEs; npm-like ecosystems make "ten thousand transitive dependencies" the norm, which is out of proportion to any reasonable trust budget.

**How to comply.**
- The standard library / already-included dependencies — the first candidate; a new one — only with a real need.
- New-dependency checklist: project activity, number of transitive dependencies, license, known CVEs, availability of alternatives; the answer — a brief record in the PR.
- Do not pull in "a framework for one function"; do not carry two tools of the same purpose.
- Updates — regular and in small steps (CI audit — G3); pinning + lockfile are mandatory.

**Applicability.** [MANDATORY] all classes.

**Automation.** Lockfile check in CI, CVE audit (`osv-scanner`/`npm audit`/`cargo audit`/`pip-audit`), license scan, capping dependency-count growth — a signal.

**Exceptions.** Urgent dependencies during incidents — added with a mark and a revision within the sprint.

---

## E6. [MANDATORY] Single source of truth for rules

**Requirement.** Business rules, formulas, validations, protocol constants exist in one place. A copy of a rule in a second place is a defect even if it currently matches: divergence is a matter of time.

**Problem.** Duplicated logic is the classic cause of "fixed in one place, broke in another". Duplication between languages/layers is especially insidious (client- and server-side validation, a formula in the backend and in a report).

**How to comply.**
- Shared logic — into a shared lower-layer module; consumers import it.
- Duplication between languages — via generation from a single specification (schema → code), not a manual copy.
- Rewriting the same logic "slightly differently" for a new context — first the question: can one implementation be parameterized?
- Deliberate duplication of small pieces beats a false "shared abstraction" with seven flags (E2): duplicated code != coupled logic. The boundary: is *text* duplicated (ok, until the third time) or a *rule* (not ok).

**Applicability.** [MANDATORY] all classes.

**Automation.** Partial: duplicate detectors (jscpd, PMD CPD) catch text duplicates but not differently rewritten copies of a rule; the rule's essence is better covered by arch tests "validation/formulas are imported only from the shared module" and schema generation in CI (generated code does not diverge). Full mechanical checking is impossible — the rest is review.

**Exceptions.** Small, weakly coupled fragments (constant literals in tests) — duplication is acceptable and often better than coupling.

---

## E7. [COND] Backward compatibility where consumers exist

**Requirement.** Public APIs, data formats, protocols, persistent schemas — are changed with existing consumers in mind: versions, a deprecation period, data migrations. "Broke the format — update everyone" is acceptable only if all consumers are in one repository and one deployment.

**Problem.** Irreversible changes to public contracts are the most expensive architecture mistake: its cost grows with the number of consumers and is invisible at commit time.

**How to comply.**
- Classify: an internal contract (within one release) — free; an external one (other teams, persisted data, clients) — versioned.
- Deprecation: announce → support in parallel → remove on schedule; never silently.
- Storage formats: additive changes only, or explicit migrations with a test on old data.

**Applicability.** [COND]: applies when external consumers exist; in a monorepo with atomic deployment — softer (but the check "all consumers updated" is mandatory).

**Automation.** API-diff in CI (E4), migration tests on copies of real data, contract tests (consumer-driven contracts).

**Exceptions.** — (the rule is determined by the presence of consumers, not by desire).

---

# Domain F. Testing and verification

## F1. [MANDATORY] Test pyramid and deterministic tests

**Requirement.** Logic is covered by fast unit tests, module interactions — by integration tests, key user scenarios — by a small number of e2e tests. All tests are deterministic: a "flaky" test is a defect of the test or the code and must be fixed, not re-run.

**Problem.** An inverted pyramid (everything through e2e) gives slow, fragile feedback; flaky tests teach the team to ignore a red pipeline — and it stops being a gate.

**How to comply.**
- Unit: milliseconds, no network/clocks/disk; integration: real adapters in an isolated environment; e2e: smoke scenarios.
- Flaky tests: recorded in the tracker, fixed in priority order; a systematically "re-run" test is deleted or marked as a known defect.
- Tests do not depend on execution order or external state.

**Applicability.** [MANDATORY] К1/К2; for К3 — at minimum smoke tests.

**Automation.** CI: unit run on every commit, integration — on PR, e2e — on PR/night; flaky detectors (re-running failures with statistics recorded).

**Exceptions.** Visual-regression tests with a controlled tolerance; external integrations unavailable in CI — via contract tests/stubs, fixed explicitly.

---

## F2. [MANDATORY] Static analysis and "fix the code, not the warning"

**Requirement.** The compiler, linter, type checker, and static analyzer are enabled from day one at maximum strictness; the code builds and analyzes without warnings. Warning suppression — only point-wise, with justification (every suppression is a separate decision, visible in the code). A dubious warning is eliminated by rewriting the code until trivially correct — the NASA requirement verbatim (rule 10: "even if the analyzer is wrong — rewrite the code that caused the confusion").

**Problem.** NASA rule 10: "there is no excuse for not using" static analyzers; "many developers considered a warning erroneous — and later were convinced it was justified for a non-obvious reason". Accumulated warnings mask new ones: the signal drowns in noise.

**How to comply.**
- Strict settings from the first commit; for existing repositories — the ratchet rule: the baseline is fixed, new warnings are prohibited (see `QUALITY_GATES.md`).
- Suppression (`# noqa`, `// nolint`, `#[allow]`, `@SuppressWarnings`) — with a reason ID in the comment; mass suppressions and lint-config edits "to make it pass" — prohibited (see H4).
- К1-additional tools: sanitizers (ASan/UBSan/TSan), verifiers.

**Applicability.** [MANDATORY] all classes; tool-set depth — by class (see `QUALITY_GATES.md`).

**Automation.** This is itself automation: F2 gates in CI, blocking.

**Exceptions.** Generated code — separate settings; false-positive suppressions — via `EXCEPTIONS_POLICY.md`.

---

## F3. [RECOMMENDED] Strict typing where available

**Requirement.** In statically typed languages — maximum strict mode; in dynamic ones — where checkers exist (mypy/ty for Python), on modified modules. Bypasses of the type system (`any`, `as unknown`, `unsafe` casts) — only with local justification.

**Problem.** Half-hearted typing gives the costs of types without their benefits: every `any` is a hole through which a defect passes to runtime.

**How to comply.**
- Enable strict flags in the project config, not "where it worked out".
- Types for boundaries (D2) and for domain values (D1); less primitive obsession — but also fewer "stringly typed" contracts.
- Every cast/bypass — with a comment "why it is safe".

**Applicability.** [RECOMMENDED] everywhere; [MANDATORY] for new К1/К2 modules.

**Automation.** tsc strict, mypy strict, clippy, warning-as-error modes — CI gates.

**Exceptions.** Legacy modules — gradual enabling along module boundaries (per-module strict), fixed in the adoption plan.

---

## F4. [COND] Property-based testing

**Requirement.** For components with verifiable invariants (parsers/serializers, sorts, aggregations, converters, cryptographic wrappers) — property-based tests: input generation + invariant checking (e.g., round-trip: `decode(encode(x)) == x`; monotonicity; completeness). The test count — a regular run, not a one-off event.

**Problem.** Example-based tests check what the author already thought of; property-based testing checks a class of inputs and finds cases a human did not recall. This is an automated analogue of NASA's "check density" idea (rule 5): more meaningful checks — more intercepted defects.

**How to comply.**
- Properties are formulated as invariants, not as "repeat the unit test with another number".
- A property-test failure must leave a minimal counterexample (frameworks do this) — it is kept as a regression example (F6).
- Do not formulate properties trivially identical to the implementation ("the call returned what the call returned").

**Applicability.** [COND]: where the invariant is meaningful. For parsers of external data — de facto mandatory (together with F5).

**Automation.** A quick run on PR (hundreds of examples), a deep nightly one (thousands); seeds in reports.

**Exceptions.** Components without formulating properties — classic tests only; that is fine.

---

## F5. [COND] Fuzzing of input parsers

**Requirement.** Code that parses untrusted data (network protocols, file formats, headers, nested structures) is tested by fuzzing in a regular (nightly) mode with a corpus collector and with sanitizers (for C/C++/Rust — ASan/UBSan mandatory).

**Problem.** A parser is the most attacked code: memory corruption and DoS are found exactly there. Fuzzing finds what neither the test author nor a property generator can conceive: uninstantiable pathological inputs.

**How to comply.**
- Fuzzing targets — parser entry points, not the whole application.
- Corpus: production examples + found crashes (each — a regression test).
- A found crash is a code defect, not a "fuzzer quirk": a minimal reproducing input into unit tests.

**Applicability.** [COND]: mandatory for parsers of untrusted К1/К2 inputs; for К3 — optional.

**Automation.** libFuzzer/AFL++, go-fuzz, OSS-Fuzz-compatible targets; nightly jobs in CI.

**Exceptions.** Parsers of only trusted, schema-validated data (an internal bus with a strict schema) — property-based instead of fuzz.

---

## F6. [MANDATORY] Regression as a test

**Requirement.** Every fixed defect is accompanied by a test that reproduces it and failed before the fix. "Fixed it, did not add a test" — unfinished work. The exception — a defect not expressible as a test — only as an E-C deviation: a record in `EXCEPTIONS.md` (an `EX-…` ID, a verifiably formulated cause — what exactly is not reproducible and why, a compensating control, a review deadline), an anchor in the code, reviewer confirmation. Until the deviation is closed, the defect counts as open.

**Problem.** A defect not fixed by a test returns (almost always — via a regression during adjacent refactoring). A regression test is the cheapest insurance: it writes itself at the moment the defect is best understood.

**How to comply.**
- Workflow: reproduce with a test (red) → fix (green) → keep the test.
- A minimal test: no extra context, with a comment referencing the task/incident.
- The deviation "not expressible as a test": non-expressibility is formulated verifiably and confirmed by a reviewer; the Q-14 gate does not close the task without a test or a valid EX (the anchor and deadline are seen by Q-19).

**Applicability.** [MANDATORY] all classes.

**Automation.** The review checklist "a defect without a test?"; coupled with the tracker (an issue link in the test).

**Exceptions.** Reproducibility defects (environment dependence) — via an E-C deviation (see the Requirement); until it is closed the defect counts as open and is checked manually per protocol.

---

## F7. [COND] Benchmarks of critical paths

**Requirement.** Paths with budgets (B5) are covered by maintainable benchmarks; their results are tracked (C6). A benchmark is code in the repository, not a "temporary script on a laptop".

**Applicability.** [COND]: exists when budgets exist.

**Automation.** Criterion/pytest-benchmark/benchstat/JMH; comparison in PR on signal, nightly tracking.

**Exceptions.** — (no budget — no benchmark).

---

## F8. [MANDATORY] CI gates — the sole enforcer of the standard

**Requirement.** All mandatory requirements of the standard that can be checked automatically are checked automatically and block merging. Compliance with the standard is not based on instructions to the agent, team memory, or "common sense". The list of gates, modes, and thresholds — in `QUALITY_GATES.md`.

**Problem.** Rules existing only in text are not enforced (the main lesson of the original: "existing guidelines rarely influence what developers actually do; the fatal flaw — the impossibility of full automatic checking").

**How to comply.**
- Every [MANDATORY] principle has either an automatic gate or a review-checklist item (and then this is fixed explicitly in `QUALITY_GATES.md`).
- A gate that can be bypassed "by agreement" is marked as soft; hard enforcement — only via `EXCEPTIONS_POLICY.md`.

**Applicability.** [MANDATORY] all classes; the gate set differs across classes К1–К3.

**Automation.** Trivially: this is the automation.

**Exceptions.** — (the exception mechanism itself is described in `EXCEPTIONS_POLICY.md`).

---

# Domain G. Security

## G1. [MANDATORY] Secure defaults

**Requirement.** A component in its "out-of-the-box" configuration is secure: deny-by-default in access checks, encryption enabled, debug endpoints disabled, verbose errors not exposed, CORS/cookies restricted. Weakening — only by an explicit action with justification.

**Problem.** A "default" vulnerability is exploited in every installation where the config was not changed (that is, in almost all of them). The reverse setting "make it secure after deployment" is never performed.

**How to comply.**
- Defaults: TLS mandatory, HttpOnly/Secure/SameSite cookies, minimum permissions, anonymous access — an allow-list, not "everything except".
- Debug/administrative surfaces — behind a flag disabled in production.
- User-facing error messages — without internal details (stacks, SQL).

**Automation.** Configuration tests ("the default deploy passes the checklist"), config scanners (checkov/tflint for IaC), review of defaults when adding features.

**Applicability.** [MANDATORY] К1/К2; К3 — per the hygiene minimum.

**Exceptions.** Local development tools — with an explicit "not for production" and configuration marking.

---

## G2. [MANDATORY] External data is hostile

**Requirement.** All external data is treated as hostile: validation at the boundary (D2), safe parsers (no `eval`, no arbitrary deserialization, no query building by concatenation), output escaping by context (HTML/SQL/shell/paths), volume limits (B6).

**Problem.** Injections (SQL/command/template), deserialization of untrusted data, XSS, and path traversal remain in the top of exploited vulnerability classes; almost all of them result from "data from the network entered an interpreter without a boundary".

**How to comply.**
- Parameterized queries / ORM — by default; SQL/command concatenation — prohibited.
- Deserialization of untrusted data — only via safe formats and safe modes (no native object deserializers).
- Output — escaped context-dependently (templating engines with auto-escaping).
- Paths from external data — normalization and a check against escaping the root.

**Automation.** SAST scanners (Semgrep/CodeQL), dependency audit (principle G3, gate Q-08), fuzzing of parsing points (principle F5), tests with canonical injections in the boundary matrix (principle D6).

**Applicability.** [MANDATORY] all classes.

**Exceptions.** Deliberate release into a trusted perimeter — with a record in exceptions and a justification of trust (trust is a property with an expiry, not a constant).

---

## G3. [MANDATORY] Dependency security and version hygiene

**Requirement.** The dependency tree is audited automatically: known CVEs block the build (or require a registered exception with an applicability assessment), versions are pinned by lockfile, updates are regular. The tree's composition is minimal (E5).

**Problem.** Most exploited application vulnerabilities are in dependencies, not in one's own code; a CVE-announced vulnerability is exploited the faster the longer the project "never got around to updating".

**How to comply.**
- CI audit on every PR and weekly (new CVEs in existing versions appear without your changes).
- Critical vulnerabilities — blocking; the rest — with a tracker and a deadline.
- Minimize the tree: every dependency is an attack surface (see E5).

**Automation.** osv-scanner/dependabot/renovate/audit tools of the ecosystems; the gate in `QUALITY_GATES.md`.

**Applicability.** [MANDATORY] К1/К2; К3 — weekly audit without blocking.

**Exceptions.** CVEs not applicable to the usage configuration — via `EXCEPTIONS_POLICY.md` with justification and a review deadline.

---

## G4. [MANDATORY] Secrets management

**Requirement.** Secrets (passwords, keys, tokens) do not end up in source code, configuration files in the repository, logs, or error messages. Delivery — from a secret store or the deployment's environment variables. Repository scanning — automatic.

**Problem.** A secret in git history is compromised forever (history cannot be "deleted" without rewriting and rotation); a leak through logs is the most frequent "accidental" leak. For AI agents — an additional risk: a secret in the task context can end up in generated code or session logs.

**How to comply.**
- No `password = "..."` in code; config — via env/secret store, with a presence check at startup.
- Logs mask secret fields; errors do not contain the contents of requests with tokens.
- A leak happened anyway — rotate immediately, regardless of "how important it was".

**Automation.** gitleaks/trufflehog in pre-commit and CI; the test "logs contain no secrets" on typical scenarios.

**Applicability.** [MANDATORY] all classes, without exceptions (this is a gate that admits no exception).

---

## G5. [MANDATORY] Least privilege

**Requirement.** Every component runs with the minimum necessary rights: an unprivileged container user, scoped tokens, granular DB permissions, minimal cloud roles. A component must not be able to do what its functionality does not require.

**Problem.** Compromise of any component under broad rights becomes compromise of the system; under minimal ones — it is localized. An attack through a dependency (supply chain) is effective exactly as far as the process's rights are broad.

**How to comply.**
- Segment secrets and rights by service; "one shared admin token for all" — prohibited.
- The application's DB user: no DDL rights in production; migrations — a separate role.
- Containers: non-root, a read-only filesystem where possible, the service account disabled by default.

**Automation.** IaC policies (deny by default), tests "the process cannot write outside its paths", role audit at review of infrastructure PRs.

**Applicability.** [MANDATORY] К1/К2; К3 — minimum: do not run as root.

**Exceptions.** Deliberate privileges (a CI deployer) — with an explicit list of "what it may do" and an audit of usage.

---

## G6. [RECOMMENDED] Fault tolerance and graceful degradation

**Requirement.** Interactions with unreliable parties (network, external services, hardware) are designed: timeouts (B6), retries with exponential backoff, jitter, and a hard maximum, idempotent retries, circuit breakers at system boundaries, degradation with partial functionality instead of cascading failure.

**Problem.** Without retries a random network glitch becomes a user-facing error; without retry limits — an avalanche of load (a "retry storm"); without circuit breakers the failure of one dependency takes down the whole service.

**How to comply.**
- Retry — only for idempotent operations, with a maximum of attempts and a deadline for the whole operation.
- Circuit breakers — on external dependencies whose failure is probable and costly.
- Degradation is thought through: what does the user see if the recommendation system is down? (the regular catalog — an acceptable answer).

**Applicability.** [RECOMMENDED] К2 services; [MANDATORY] for К1 where availability is a contract property.

**Automation.** Chaos/failure tests (a mock "the dependency answers 500/timeout"), the D6 boundary matrix; in review — the checklist "timeout/retry/degradation".

**Exceptions.** Operations where a retry is dangerous (a money transfer without receiver-side idempotency) — designed via idempotency keys, not "without retries".

---

# Domain H. Requirements for AI development agents

Domain H defines the agent's behavior (a human with an AI assistant or an autonomous agent) when working with the code base. The domain's peculiarity: most requirements cannot be secured by "instruction and hope" — they are backed by gates (`QUALITY_GATES.md`), the PR structure, and the review checklist. The formulations are prohibitions (prohibited actions are easier to check than required intentions).

## H1. [MANDATORY] Task boundaries: do not rewrite unrelated code

**Requirement.** Changes are bounded by the task. Incidental improvements (refactoring "while at it", renames, reformatting of others' files, updates of unrelated dependencies) — are not done silently: either not done, or split into separate PRs with their own task.

**Problem.** Unrelated changes: (a) make the diff unreviewable — a reviewer misses defects in the noise; (b) break `git blame`/bisection; (c) carry the risk of unrelated regressions into a "safe" task. For agent workflows this is critical: an agent can "improve" half the file system in one task.

**How to comply.**
- Before changing a file outside the explicit list — stop: is it required by the task? If not — do not touch it.
- Noticed an adjacent defect — record it as a separate task/comment, do not fix it in passing.
- Auto-formatting — only on files touched by the task (or a separate "formatting" PR with a logic-empty diff).

**Automation.** Diff-size capping as a signal; the check "changed files ⊆ task files" in the PR template; review.

**Exceptions.** Mass mechanical changes (an API rename) — in a separate PR, with an automated "the diff is mechanical" check.

---

## H2. [MANDATORY] No speculative abstractions or architecture expansion beyond the task

**Requirement.** The agent does not introduce abstractions, layers, configuration mechanisms, or "support for future cases" outside the task requirements. The solution is minimally sufficient for the task. "It seemed like it might be useful" is not a reason.

**Problem.** A speculative abstraction is negative value: code nobody asked for, nobody needs, but everybody must maintain, test, and read. Agents are especially prone to this pattern (generalizing a special case into a "universal mechanism").

**How to comply.**
- A concrete solution for a concrete task (see E2, the "two implementations" rule).
- Before adding an interface/class/layer — answer: what second implementation exists *now*? None — do not add it.
- "Extensibility" is added when the second requirement arrives; then it is visible as a fact, not a fantasy.

**Automation.** The signal "a new interface with one implementation and one consumer" in review; the checklist.

**Exceptions.** The task requirement explicitly describes variability ("must support A and B") — then the variability is concrete, not speculative.

---

## H3. [MANDATORY] No silent changes to public interfaces and contracts

**Requirement.** Changing a public API, data format, schema, protocol, or the semantics of existing methods — only deliberately: highlighted in the PR description, assessed for compatibility (E7), approved (if there are external consumers). "Incidentally changed the signature/behavior" — prohibited.

**Problem.** A public contract is a promise to consumers. A silent change breaks client builds, serialized data, and integrations not at commit time but at the consumer's next update — when the link to the change is lost.

**How to comply.**
- A PR changing a public API contains a "Contract changes" section with migration.
- Internal reuse of an API beyond its purpose (reaching into private fields, bypassing invariants) — treated as a contract change.
- Automated contract tests signal changes.

**Automation.** API-diff in CI (mandatory for libraries); review.

**Exceptions.** — (the change is not prohibited; it is the *silence* that is prohibited).

---

## H4. [MANDATORY] Do not weaken checks to "make it green"

**Requirement.** Passing gates by changing the gates themselves is prohibited: disabling/weakening linters and types in config, mass `nolint`/`noqa`/`#[allow]`, lowering test log levels, disabling sanitizers, adding exceptions to CI configuration — in order to pass a check. Suppressing a specific false positive is allowed only point-wise, with a justification comment (see F2, `EXCEPTIONS_POLICY.md`).

**Problem.** A "green pipeline" has value only with fixed thresholds. An agent (and a human under deadline pressure) is tempted to "switch off the flashing light" instead of fixing the defect — after that the pipeline stops catching defects at all.

**How to comply.**
- A red gate → diagnose the defect → fix the code.
- Convinced the trigger is false? Point suppression with a comment "why it is false and why it is safe". Changing global lint configuration is not a way to "fix" a warning; it is a change of the standard — via `EXCEPTIONS_POLICY.md`.
- A test failed due to "environment instability"? Re-run — with the fact recorded (see F1), not deleting the test.

**Automation.** A separate gate "the diff does not change gate configuration" (a guard gate): files `.lintcfg`, `eslint.config`, `Cargo.toml [lints]`, CI workflows — require a label and enhanced review; counting suppressions — growth beyond the baseline — a signal.

**Exceptions.** Via `EXCEPTIONS_POLICY.md`, with a human sign-off.

---

## H5. [MANDATORY] Do not bend tests to fit defective code

**Requirement.** A test is changed only if it is proven that the test itself is defective (an outdated expectation, an error in the test, changed requirements). Bending expectations to match the actual (defective) behavior of the code — "made the test green without understanding why" — is prohibited and counts as a more serious violation than a red test.

**Problem.** A test is the oracle of correctness. A test rewritten to fit defective code turns the verification system into camouflage: formally everything is green, in fact the regression is recorded as "correct behavior".

**How to comply.**
- The test is red → first the question: "what should the code do per the requirements?" The answer comes from requirements, not from actual behavior.
- Changing a test — explain in the PR: "the test was wrong because…" with proof (a link to the requirement/spec/owner confirmation).
- Golden files/reference values are updated only together with a justified change of the golden reference (see H8).

**Automation.** Partially mechanical: tests are protected paths (CODEOWNERS); a diff with tests gets the `test-change` label (set by a bot from the diff); deleting a test, moving it to skip/xfail, reducing the number of checks, new golden/snapshot references in the same PR as the code — require a second reviewer (gates Q-10/Q-12). For К1 and critical modules — point mutation testing in nightly runs (a mechanical check of test strength). Full "bending" is not caught by mechanics — a recognized limitation, compensated by review.

**Exceptions.** An explicit change of requirements — with the specification changed *before* the tests.

---

## H6. [MANDATORY] Do not claim verification you did not perform

**Requirement.** Claims of operability ("tests pass", "it builds", "checked manually") are made only based on actually executed commands, with real output. Faking verification (invented output, "it should work", skipping a run with the wording "verified") — a critical violation, equated to sabotage.

**Problem.** An agent reporting "done, tests are green" without a run injects incorrect code with a false certificate of trust — worse than an honest "did not check": the consumer stops verifying themselves. For autonomous agents this is the most dangerous violation class, because it is invisible in the diff.

**How to comply.**
- Checks covered by CI: claiming "passed" with a red pipeline is prohibited — this is a mechanically detectable violation (gate Q-15). The status is taken from CI, not from the report text.
- Checks outside CI (manual scenarios, external environments): the result — a reproducible artifact (command + run ID/output hash, which a reviewer or bot can re-run), not an "excerpt of text".
- Could not execute — record explicitly "not verified: reason" and what is needed for verification. This is a legitimate outcome; faking — is not.

**Automation.** Gate Q-15: (a) a claim about a CI-covered check with red CI — a red PR; (b) for non-pipeline checks — a link to a reproducible artifact is mandatory; (c) mentioned commands must exist in the repository's scripts/configuration (checked by a bot).

**Exceptions.** — (none).

---

## H7. [MANDATORY] No undocumented assumptions about requirements

**Requirement.** Ambiguity in requirements is resolved not by a silent choice but by a question (see the stop conditions in `QUALITY_GATES.md`) or — if the task admits a working assumption — by an explicit assumption record marked "requires confirmation". Silent interpretation of "the way I understood it" — prohibited.

**Problem.** An agent that "guessed" a requirement solves a different task, possibly destroying adjacent logic; the cost of the error grows with the pipeline stages passed.

**How to comply.**
- Before starting: list what you understand as input/output/constraints; uncertainties go into questions.
- A working assumption is acceptable when: it is formally reversible (does not change the public API surface, persisted data, golden references — detected by gates Q-10/Q-12), documented in the task and PR, and entered into the assumption register with an owner and a deadline.
- Confirmation: the owner answers within the task deadline; an assumption unconfirmed past the deadline blocks task closure and escalates.

**Automation.** An "Assumptions" field in the task template (owner + deadline); a stop event is recorded with the marker `[STOP: H7]` and the task status `question` (see `QUALITY_GATES.md` §6); the review checklist "assumptions confirmed?".

**Exceptions.** Trivial tasks with a single reasonable interpretation — without ceremony; the boundary — the risk of changing a contract/data.

---

## H8. [MANDATORY] Do not change established mathematical, financial, and business rules without explicit permission

**Requirement.** Reference values (golden files), calculation formulas, business-rule constants, tax/tariff tables, and compliance rules are not changed within ordinary tasks. Such a change is a separate task with explicit authorization from the rule's owner, an updated specification, and a recorded justification.

**Problem.** "Fixed the number so the test would agree" — a classic agent error with the maximum price: money calculations, reporting, regulatory compliance. The difference from H5: here the defect may be not in the code but in the requirement — and deciding that is not the developer's job.

**How to comply.**
- Noticed a divergence of code from the expected golden reference? Stop and raise a question; do not "fix" silently — neither the code nor the reference.
- Changing a rule — via a task with the domain owner's confirmation; in the PR — a quote of the confirmation.

**Automation.** Golden-reference files are marked with CODEOWNERS of mandatory owners; a guard gate: a diff of golden files requires the "rule change" label and a second reviewer.

**Exceptions.** — (the rule itself is a form of exception — an authorized one).

---

## H9. [MANDATORY] Diff self-review and honest reporting before submission

**Requirement.** Before completing a task the agent must: (1) re-read its full diff as a reviewer; (2) run the gates available in its environment (build, unit tests, lint) — really, with output (H6); (3) verify compliance with task boundaries (H1); (4) in the report, separate facts (what was done and verified) from unconfirmed expectations (what "should work" but was not verified).

**Problem.** The quality of agent work is determined not by "generation boldness" but by the discipline of checking; an unread own diff is a source of "one's own" defects (truncated imports, broken adjacent tests, forgotten generation artifacts).

**How to comply.**
- The submission checklist — a single source: the mini-checklist in `AI_AGENT_RULES.md`, also included in the PR template; no duplicates in other documents.

**Automation.** The PR template (from the same source as the checklist); gate Q-15; the session's stop-event log; review.

**Exceptions.** — (none).

---

# Relation to other standards and sources

## Related standards

This document does not replace language standards but sets the frame:

- **MISRA C:2012 / MISRA C:2023** — for К1 C code (a language subset for verifiability); Power of 10 historically complements MISRA.
- **SEI CERT C/C++, Java, Secure Coding** — detailing of security rules by language.
- **OWASP ASVS / OWASP Top 10** — security checklists for web applications (refining domain G).
- **Project language styles** (Google Style Guides etc.) — formatting and idioms; deliberately not duplicated here.
- **JPL Institutional Coding Standard for the C Language (JPL, 2009)** — the practical embodiment of Power of 10 in C; useful as a reference for К1 C code.

## Sources

1. G. J. Holzmann. *The Power of 10: Rules for Developing Safety-Critical Code*. IEEE Computer, 39(6), pp. 95–99, June 2006. DOI: 10.1109/MC.2006.212. (NASA/JPL Laboratory for Reliable Software.)
2. JPL Institutional Coding Standard for the C Language. JPL Laboratory for Reliable Software, 2009.
3. NASA Engineering and Safety Center. *Technical Assessment Report: National Highway Traffic Safety Administration Toyota Unintended Acceleration Investigation* (Appendix A: firmware analysis against the Power of 10 rules, ≥243 violations), 2011.
4. MISRA C:2012 / MISRA C:2023. Guidelines for the use of the C language in critical systems. MISRA.
5. SEI CERT Coding Standards (C, C++, Java, Perl, Android). Carnegie Mellon University, SEI.
6. OWASP Application Security Verification Standard (ASVS). OWASP Foundation.

---

# Final status table of requirements

| ID | Principle | Class | Gate |
|---|---|---|---|
| A1 | Simple control-flow constructs | MANDATORY | partially auto (lint) + review |
| A2 | Bounded recursion | COND | depth tests, fuzz |
| A3 | Iteration bounds | MANDATORY | CI timeouts, review |
| A4 | Complexity thresholds as triggers | RECOMMENDED | warning + ratchet on changed functions (Q-02) |
| A5 | Explicit state transitions | merged into A1 | — |
| A6 | Minimal scope | MANDATORY | lints partially |
| A7 | Feature-flag and conditional-compilation discipline | RECOMMENDED ([MANDATORY] for К1) | CI variant matrix, directive counting |
| B1 | Predictable and bounded memory consumption (absorbed B2, B4) | MANDATORY | by project class + sanitizers/load tests |
| B2 | Frugal copying | merged into B1 | — |
| B3 | RAII resource lifecycle | MANDATORY | lints, sanitizers |
| B4 | Leak control | merged into B1 | — |
| B5 | Resource budgets | RECOMMENDED | benchmarks |
| B6 | External-interaction limits | MANDATORY | lints + tests |
| C1 | Deliberate complexity (absorbed C2, C3) | RECOMMENDED | review + volume tests |
| C2 | Do not repeat computations | merged into C1 | — |
| C3 | Appropriate data structures | merged into C1 | — |
| C4 | No premature optimization | RECOMMENDED | review |
| C5 | Profile before optimizing | RECOMMENDED | PR procedure |
| C6 | Performance-regression protection | COND | nightly benchmarks |
| D1 | Explicit contracts | RECOMMENDED | types + assert lint |
| D2 | Input validation + error handling (absorbed D3) | MANDATORY | schemas + error lints |
| D3 | Complete error handling | merged into D2 | — |
| D4 | Numerical correctness | COND | lints + property |
| D5 | Managed determinism | COND | seeded tests |
| D6 | Boundary cases | RECOMMENDED | test matrices + property/fuzz (partially) |
| E1 | Separation of concerns | merged into E3 | — |
| E2 | Minimum abstractions | MANDATORY | review signal |
| E3 | Modularity: dependencies and responsibility (absorbed E1) | MANDATORY | arch tests (imports) |
| E4 | Minimal API | RECOMMENDED | api-diff |
| E5 | Dependency discipline | MANDATORY | audit + lockfile |
| E6 | Single source of rules | MANDATORY | arch tests + duplicate detectors (partially) |
| E7 | Backward compatibility | COND | api-diff, migrations |
| F1 | Test pyramid | MANDATORY | CI |
| F2 | Static analysis, zero new | MANDATORY | CI |
| F3 | Strict typing | RECOMMENDED | CI |
| F4 | Property-based | COND | nightly |
| F5 | Parser fuzzing | COND | nightly |
| F6 | Regression as a test | MANDATORY | review |
| F7 | Benchmarks of critical paths | COND | nightly |
| F8 | CI gates | MANDATORY | CI |
| G1 | Secure defaults | MANDATORY | config tests |
| G2 | External data is hostile | MANDATORY | SAST + fuzz |
| G3 | Dependency security and version hygiene | MANDATORY | CVE audit |
| G4 | Secrets | MANDATORY | gitleaks etc. |
| G5 | Least privilege | MANDATORY | IaC policies |
| G6 | Fault tolerance | RECOMMENDED ([MANDATORY] for К1 with contract availability) | failure tests |
| H1 | Task boundaries | MANDATORY | procedural: PR template + review; partially Q-16 |
| H2 | No speculative abstractions | MANDATORY | procedural: checklist; Q-09 signal |
| H3 | No silent API changes | MANDATORY | api-diff |
| H4 | Do not weaken checks | MANDATORY | guard gate |
| H5 | Do not bend tests | MANDATORY | procedural + Q-10/Q-12 (second review), mutation for К1 |
| H6 | Honest verification | MANDATORY | verification log |
| H7 | No undocumented assumptions | MANDATORY | procedural: stop artifact + assumption register |
| H8 | Do not change rules without permission | MANDATORY | CODEOWNERS/guard |
| H9 | Self-review and honest report | MANDATORY | procedural: PR template + session log; Q-15 partially |

*Automation statuses: "partially auto" — a combination of mechanics and judgment; the full distribution — in `QUALITY_GATES.md`. Rules marked "procedural" are enforced by review and process artifacts — recognized limitations; their share is published as a maturity metric of the standard (see `QUALITY_GATES.md` §6).*
