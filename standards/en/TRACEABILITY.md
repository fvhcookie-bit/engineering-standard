# TRACEABILITY
## Correspondence between the original NASA/JPL rules and the adapted standard

**Version:** 1.2 · **Purpose:** transparent tracing of every change to the original. The task's requirement — "do not attribute invented requirements to NASA" — is fulfilled by this document.
**Official translation.** The authoritative text is the Russian original (`standards/TRACEABILITY.md`); in case of divergence the Russian wording prevails. The original quotes in §2.1 are kept verbatim.

The primary source: `P10.pdf` (stored outside the repository, in the owner's local archive). The quotes in the §2 table are the authors' translation; the original anchors (EN) for mechanical verification — in §2.1.

---

## 1. The original source

**G. J. Holzmann. The Power of 10: Rules for Developing Safety-Critical Code.** IEEE Computer, vol. 39, no. 6, pp. 95–99, June 2006. DOI: 10.1109/MC.2006.212. NASA/JPL Laboratory for Reliable Software, Pasadena, CA.

Key facts about the original (from the article's text):

- The rules are written **for C code** in protected systems: "our rules are oriented primarily toward C and optimized for maximum scrutiny of the reliability of critical applications written in C".
- The goal is not style but **verifiability by tools**: "a rule set should be small and clear enough to be easily memorized… specific enough to be mechanically checked".
- The rules are deliberately strict: "the rules are somewhat strict — one might even say 'draconian'. The compromise should be obvious… when it really matters, it is worth going the extra mile".
- The rules were applied **experimentally** at JPL: "these ten rules are being used experimentally for writing mission-critical software with encouraging results".
- A known application: the NESC (NASA Engineering and Safety Center) analysis of the Toyota electronic throttle firmware (2011) recorded ≥ 243 violations of these rules.

## 2. The summary traceability table

Notation of changes: **preserved** (transferred without substantial changes) · **strengthened** (the requirement extended) · **weakened** (unique constraints softened while preserving the goal) · **reinterpreted** (the goal preserved, the mechanism replaced) · **localized** (a universal requirement made contextual).

Statements in the "Justification of the change" column not backed by an external reference — are adaptation justifications (the compilers' position), not quotes from the source.

| # | The NASA rule (paraphrase) | The original's goal | The standard's principles | Change | Justification of the change |
|---|---|---|---|---|---|
| 1 | Only simple control-flow constructs; `goto`, `setjmp`/`longjmp`, and direct or indirect recursion banned | An acyclic call graph, static verifiability of paths, comprehensibility | A1, A2 | Weakened + localized | `goto` for resource cleanup is a recognized C idiom (the Linux kernel, Documentation/process/coding-style.rst, ch. 7 "Centralized exiting of functions"); a full ban in modern languages with RAII/exceptions yields no benefit; `setjmp/longjmp` is replaced by language error-handling mechanisms. Recursion: in modern languages DFS algorithms are natural; the original goal (bounded stack, provability) is preserved via an explicit depth limit — A2. Control-flow analyzability remains a goal of A1 |
| 2 | All loops have a statically provable upper bound; the exception — loops designed to be non-terminating (with a reverse requirement) | Exclusion of "runaway" code, a termination guarantee | A3, B6 | Reinterpreted + extended | Static provability is often unachievable in dynamic and event-driven systems, but the goal (no infinite/hanging loops) is achieved by explicit guard limits and timeouts; extended to modern realities — unbounded external input (network, files) as a source of infinite iterations. The original's exception for non-terminating loops is preserved (A3) with the addition of a timeout/progress requirement |
| 3 | Dynamic memory allocation after initialization banned | Unpredictability of allocators/GC; the malloc/free error class; a provable memory bound | B1, B3, B4 | Localized | For К1 (real-time/embedded) preserved verbatim. For К2+ formulated as "predictability and boundedness": a full ban is impossible in managed environments (GC, managed runtimes) where allocations are built into any code; the real goal — predictable consumption and absence of leaks — is achieved by limits (B1, B6), RAII (B3), and leak control (B4) |
| 4 | A function is no longer than one sheet of paper (≈60 lines) | A function as a logical unit, comprehended and verified holistically | A4 | Reinterpreted (a trigger) | The original itself defines the threshold heuristically ("typically about 60 lines"). A hard gate would produce splitting for the counter's sake. The threshold is kept as a trigger for mandatory explanation at review, not as a measure of quality. The goal (a holistic logical unit) — unchanged |
| 5 | Assert density on average ≥ 2 per function; asserts without side effects, boolean; explicit action on failure; meaningless asserts banned | Raising the density of early defect detection (unit tests find ≥1 defect per 10–100 LOC); elements of design-by-contract | D1, D2 | Partially reinterpreted | The quality requirements for asserts are preserved verbatim (no side effects, boolean, meaningfulness, action on failure). The "2 per function" quota is replaced by moving contracts into the type system (better than asserts: checked by the compiler) + mandatory boundary checks (D2) + the recommended contract density in К1. Reason: the quota was optimal for C without types; in typed languages it would encourage "assert stuffing" |
| 6 | Data is declared in the smallest possible scope | Data hiding; limiting the number of assignment points; reuse of variables banned | A6 | Preserved | Transferred practically verbatim, supplemented with the modern continuation of the goal — minimizing the shared mutable global scope (mutable singletons, "global state as an interface") |
| 7 | Return values of non-void functions are checked; parameter validation inside every function; permissible explicit `(void)` ignoring | Exclusion of silent failures; "the most frequently violated rule"; exceptions must be justified and visible | D2, D3, G2 | Reinterpreted + strengthened | In languages with exceptions/Result types and `must_use` annotations, return checking moves into the compiler — silent ignoring becomes impossible/flagged. Explicit ignoring with justification is preserved as a legitimate technique (explicitly described in the original). Strengthened: parameter validation is localized at system boundaries (D2) instead of "in every function" (duplication), internal ones — by contracts (D1). Strengthened by the security section (G2: external data is hostile) |
| 8 | The preprocessor — only includes and simple macros; no token-pasting, variadics, recursive macros; conditional compilation — minimal and justified | The preprocessor as "a powerful obfuscation tool"; the combinatorial explosion of code variants (2^N) | E5 (analogue), A7, QUALITY_GATES Q-02/Q-11 | Reinterpreted + supplemented | There is no direct preprocessor analogue outside C/C++; the goal — limiting the combinatorics of code variants (2^N) — is moved to modern forms: external dependency discipline (E5), the ban on build "magic", and — a new v1.1 edit — principle A7 "feature-flag and conditional-compilation discipline" (a flag owner, a removal deadline, a test of both branches, a CI matrix of variants). In C/C++ code the original rule is preserved in the project's linter settings |
| 9 | Pointers: ≤ 1 level of dereferencing; no hidden dereferences in macros/typedefs; function pointers banned | Traceability of data flow and the call graph for static analysis | A1, E3, F2 (partially) | Reinterpreted per language | In languages without explicit pointers the analogue — a ban on hidden mechanisms that break flow analysis: import-time side effects, reflection/dynamic dispatch by strings without an explicit registration point (closed by the E3 requirement of an explicit handler registry), `unsafe` blocks without justification (registered and counted by gate Q-11). In C/C++ the dereferencing limit — a project linter setting. The function-pointer ban is weakened to "requires justification and an explicit alternative for the analyzer" (the original itself allows them with "strong justification" — see its rationale) |
| 10 | Compilation with maximum warning strictness from day one, zero warnings; daily static analysis by ≥1 tool, zero findings; a dubious warning — by rewriting the code, not by disabling it | "No excuse for not using" the available analyzers; zero warnings even on false findings | F2, F8, QUALITY_GATES Q-02/Q-03/Q-06/Q-11 | Preserved + strengthened | Fully preserved, including "fix the code, not the warning". Strengthened: "daily" → "automatically on every PR" (the pipeline); ≥1 tool → a set (lint+types+analysis+sanitizers per class); the ratchet rule for legacy added (NASA's context is new mission code; for existing repositories the direct requirement of zero from day one is mechanically unachievable) |

### 2.1. Anchors of the original quotes (EN, for mechanical verification against `P10.pdf`)

1. "Restrict all code to very simple control flow constructs – do not use goto statements, setjmp or longjmp constructs, and direct or indirect recursion."
2. "All loops must have a fixed upper-bound." (in the Wikipedia paraphrase: "Give all loops a fixed upper bound")
3. "Do not use dynamic memory allocation after initialization."
4. "No function should be longer than what can be printed on a single sheet of paper…"
5. "The assertion density of the code should average to a minimum of two assertions per function."
6. "Data objects must be declared at the smallest possible level of scope."
7. "The return value of non-void functions must be checked by each calling function, and the validity of parameters must be checked inside each function."
8. "The use of the preprocessor must be limited to the inclusion of header files and simple macro definitions."
9. "The use of pointers should be restricted."
10. "All code must be compiled, from the first day of development, with all compiler warnings enabled at the compiler's most pedantic setting."

The quotes are verified against `P10.pdf` (outside the repository); the translations in the §2 table are the authors'. The Toyota/NESC reference: NESC Technical Assessment Report (2011), Appendix A (the firmware analysis against the Power of 10 rules).

## 3. What NASA does **not** say (protection against false interpretations)

These statements are often erroneously attributed to the Power of 10. The original's text asserts the opposite or is silent:

1. **A single return point is not required.** The original states directly: rule 1 "does not require that all functions have a single point of return… often an early return on error is a simpler solution". Our A1 endorses early returns.
2. **"60 lines" is not a universal measure of quality.** The original formulates the threshold as a printed-page heuristic ("typically, no more than about 60 lines") for the property "a function is a logical unit". Our A4 preserves the goal and makes the threshold a review trigger.
3. **The assert quota (≥2/function) is not mechanically transferable to all languages.** It is defined in the context of C code; in typed environments it is replaced by the type system (see D1). This is a deliberate adaptation, not a NASA omission.
4. **Rule 7 allows explicit ignoring of return values.** The original describes the `(void)` cast as a legitimate technique when "the reaction to an error does not differ from the reaction to success". Our D3 reproduces this requirement with a justification comment.
5. **Rule 2 has a built-in exception.** "Does not apply to iterations designed to be non-terminating (for example, a scheduler)" — the original text. Our A3 repeats the exception, adding the modern timeout/progress requirement.
6. **The rules are not about performance.** The Power of 10 optimizes *verifiability and reliability*, not speed; the original contains no optimization requirements. Therefore this standard contains the no-premature-optimization rule (C4) and the profiling requirement (C5) — they are in the spirit of the original ("do not complicate without need"), but not extracted from it.
7. **The rules are not about formatting.** The original criticizes rules "about spaces" as taste; our standard deliberately contains no stylistic rules — they are delegated to formatters.

## 4. Tracing the adaptation goals → principles

The seven goals from the task specification (priority order preserved):

| Goal | Implemented by the principles |
|---|---|
| 1. Functional correctness | D1–D6, A1, A5, F1, F4, F6 |
| 2. Efficiency and resource frugality | B1–B6, C1–C6 |
| 3. Maintainability and low complexity | A4, E1–E7, A5 |
| 4. Testability and verifiability | F1–F8, D6, A1–A3 (analyzability) |
| 5. Security and fault tolerance | G1–G6, B6 |
| 6. Portability and sustainability | E5, E7, A3, F2 (build matrices via CI) |
| 7. AI-agent workflows | H1–H9, F8, QUALITY_GATES (L1/L2/L3, guard gates, stop conditions) |

## 5. History of the adaptation's changes

The standard's version history is kept in the repository's single changelog — [CHANGELOG.md](../../CHANGELOG.md) (ROADMAP task A-4: a single source of history; the version table was moved there verbatim, and the current version of the core documents is mechanically verified against it — `tools/doc_consistency.py`).

Future changes to the standard (including by the exception signal — `EXCEPTIONS_POLICY.md` §6) are recorded in the changelog with justification, so that traceability remains complete.
