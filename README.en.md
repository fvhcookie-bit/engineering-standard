# Engineering Standard

An engineering standard for AI-assisted civil software development (v1.2)
and its enforcement layer (guard gates).

**Это официальный перевод.** The authoritative text is the Russian original ([README.md](README.md)); in case of divergence, the Russian wording prevails.

**Development plan:** see [ROADMAP.md](ROADMAP.md) (Russian).

## Structure

| Folder | Contents |
|---|---|
| root | `CHANGELOG.md` — the single version history of the standard and the runner (A-4); `MATURITY.md` + `MATURITY_HISTORY.md` — the maturity metric (D-3); `ROADMAP.md` — development plan |
| `standards/` | Normative core of the standard (v1.2) — see the document list below. English translations: `standards/en/` |
| `standards/review/` | Archive of independent v1.0 reviews (4 reviews, 2026-11-13) + `REVIEWS_STATUS.md` (statuses of 107 findings) + the v1.2 reduction map |
| `guidelines/` | The task specification and guidelines of the enforcement layer `gate-runner` (stages M1–M4, acceptance matrix Б-1…Б-24) |
| `tools/` | Repository service scripts: `doc_consistency.py` — consistency of the project's own documents (A-3; CI — `.github/workflows/consistency.yml`), `build_digest.py` — AI digest (B-9), `maturity.py` — the maturity metric (D-3) |
| `tooling/` | **gate-runner** — the executable enforcement layer (companion; monorepo decision by the owner, 2026-11-17; CI — `.github/workflows/tooling.yml`) |

> The original task specification (PDF) is stored outside the repository; `user/P10.pdf`-style references in TRACEABILITY point to the owner's local archive.

## Standard documents (`standards/`)

1. **ENGINEERING_PRINCIPLES.md** — 55 principles across domains A–H (48 live after the v1.2 merges; the rest are stubs kept for traceability); project classes К1–К3 (`REPO_CLASS`); carrier terms (§0.7). — **English: [standards/en/ENGINEERING_PRINCIPLES.md](standards/en/ENGINEERING_PRINCIPLES.md)**.
2. **QUALITY_GATES.md** — the executable model of checks: levels L0–L4, the ratchet rule, the gate catalog Q-01…Q-19. — **English: [standards/en/QUALITY_GATES.md](standards/en/QUALITY_GATES.md)**.
3. **AI_AGENT_RULES.md** — the rules for AI agents: task boundaries, prompt-injection protection, stop conditions, the PR checklist. — **English: [standards/en/AI_AGENT_RULES.md](standards/en/AI_AGENT_RULES.md)**.
4. **EXCEPTIONS_POLICY.md** — the deviation taxonomy E-A…E-D, the sign-off matrix, the consequences of violations. — **English: [standards/en/EXCEPTIONS_POLICY.md](standards/en/EXCEPTIONS_POLICY.md)**.
5. **IMPLEMENTATION_GUIDE.md** — the adoption procedure: 7 stages, success metrics, anti-patterns. — **English: [standards/en/IMPLEMENTATION_GUIDE.md](standards/en/IMPLEMENTATION_GUIDE.md)**.
6. **TRACEABILITY.md** — traceability to the NASA Power of 10 rules (version history — in [CHANGELOG.md](CHANGELOG.md)); anchors of the original quotes for mechanical verification. — **English: [standards/en/TRACEABILITY.md](standards/en/TRACEABILITY.md)**.

## Enforcement layer (`guidelines/`)

- **TASK_guard-gates.md** — the task specification for the companion (the `gate-runner` enforcement layer): stages M1–M4, the acceptance/bypass scenario matrix Б-1…Б-24. — **English: [guidelines/en/TASK_guard-gates.md](guidelines/en/TASK_guard-gates.md)**.
- **GUIDELINE_development.md** — the runner architecture, the gate contract, the independent-sources rule. — **English: [guidelines/en/GUIDELINE_development.md](guidelines/en/GUIDELINE_development.md)**.
- **GUIDELINE_profiles_and_dictionaries.md** — linter profiles, suppression dictionaries, config fingerprint. — **English: [guidelines/en/GUIDELINE_profiles_and_dictionaries.md](guidelines/en/GUIDELINE_profiles_and_dictionaries.md)**.

The enforcement layer's README also has a translation: [tooling/README.en.md](tooling/README.en.md).

## Companion

- **gate-runner** — the implementation of the guard gates (Q-10, Q-11, Q-12, Q-15, Q-16, Q-17, Q-18, Q-19, the L0 perimeter; profiles, dictionaries for 7 ecosystems, the metrics aggregator). Developed in this same repository: the `tooling/` directory, `runner-vN` tags (monorepo decision by the owner, 2026-11-17; extraction — when external consumers appear). See `guidelines/TASK_guard-gates.md` and `tooling/README.md` (Russian).

## Status

- **Standard v1.2** — active; the repository is public, GPL-3.0 licensed.
- **Enforcement layer (gate-runner v1.0)** — 8 gates (Q-10, Q-11, Q-12, Q-15, Q-16, Q-17, Q-18, Q-19) and the L0-perimeter detector; the Q-11 self-gate runs on every push and PR of this repository.
- **Adoption** — the owner is piloting the standard (since 2026-11-18); connecting a target repository follows `IMPLEMENTATION_GUIDE.md` (7 stages), the next operational step.
- **Feedback → revision** — deviation signals (E-C/E-D) and open review findings (`standards/review/REVIEWS_STATUS.md` §7) are the input for the next revision.

## License

[GPL-3.0](LICENSE) (GNU General Public License v3). The textual documents of the
standard (`standards/`, `guidelines/`) and the executable layer (`tooling/`) are
licensed alike. Based on G. J. Holzmann, *The Power of 10* (IEEE Computer, 2006);
traceability of borrowings — `standards/TRACEABILITY.md`.
