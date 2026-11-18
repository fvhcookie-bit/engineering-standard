# EXCEPTIONS_POLICY
## The policy of justified deviations

**Version:** 1.2 · **Purpose:** how to legitimately deviate from a requirement of `ENGINEERING_PRINCIPLES.md` without destroying the standard. A deviation is a managed and visible form of debt, not a "bypass of the pipeline".
**Official translation.** The authoritative text is the Russian original (`standards/EXCEPTIONS_POLICY.md`); in case of divergence the Russian wording prevails.

---

## 1. The basic principle

The standard is valuable because it is enforced automatically. Every exception is a local weakening of a guarantee, therefore it must be: **point-wise** (minimal coverage), **justified** (a recorded cause), **time-limited** (a review deadline), **approved** (a sign-off per risk level), and **visible** (detectable by automation, counted in metrics).

Weakening a rule by changing its global configuration is prohibited — global changes to the standard go through changing the standard itself (section 6), not through an exception.

## 2. Kinds of deviations

| Kind | What it is | Where it lives | Lifetime |
|---|---|---|---|
| **E-A. Point suppression** | Disabling a specific tool finding on a specific line | Directly in code: `# noqa: E501 # reason: long data table` (without an EX-ID; counted by gate Q-11 against the baseline) | Reviewed at file review or by a Q-11 alert |
| **E-B. Temporary baseline** | Acknowledged pre-existing legacy violations | A baseline file (ratchet config) | Decreases per plan; a concrete deadline in the adoption plan |
| **E-C. Deviation by decision** | A deliberate violation of a principle for a specific goal (compatibility, measured performance, platform constraints) | A record in the repository's `EXCEPTIONS.md` + an anchor in code (`EX-…`) | With a fixed review deadline (default ≤ 6 months) |
| **E-D. A change to the standard** | The rule is fundamentally inapplicable to the class of tasks | A PR to this standard | Permanent |

Do not confuse: **any linter/test failure** does not become an exception automatically — the falseness of the finding or the legitimacy of the violation is proven first (section 4).

## 3. Registering an exception (the form)

Every E-C exception gets an ID `EX-<year>-<NNN>` and a record:

```markdown
### EX-2026-001
- **Principle:** B6 (limits of external interactions)
- **Scope:** `services/legacy-bridge/recv.py`, function `recv_loop`
- **Essence of the deviation:** no limit on the number of messages; the guarantee is set by protocol v1 (a peer connection with its own limit)
- **Justification:** changing the protocol layer = an out-of-sprint project; the risk is bounded to the internal network
- **Compensating controls:** a response-time watchdog, an alert on queue growth
- **Sign-off:** tech lead (see section 5)
- **Review deadline:** 2026-06-01
- **Status:** active
```

The anchor in code must reference the ID:

```python
# EX-2026-001: see EXCEPTIONS.md - the message limit is set by protocol v1
```

## 4. The decision procedure

### 4.1. The algorithm for an agent/developer

1. **Diagnostics.** Is the violation real? Or is the finding false?
   - A false finding → E-A (a point suppression with a reason). A global change of tool configuration is not E-A (see 4.3).
   - A real violation → step 2.
2. **Alternatives.** Is there an executable way to comply with the rule in a reasonable time? If yes — comply, do not deviate.
3. **Risk assessment.** Which guarantees are weakened? What is the compensating control?
4. **Registration.** The form of section 3, an anchor in code, the PR label `exception`.
5. **Approval** by a sign-off (section 5).
6. **Review** at the deadline: the exception either closes (compliance) or is extended with a new justification record. Silent extension is prohibited.

### 4.2. Who confirms a tool's false finding

The falseness of a finding is confirmed by a minimal code case or a reference to the rule's documentation — not by "opinion". If a finding is disputable, it is a violation by default (F2: "fix the code, not the warning" — rewrite the code so the question disappears).

### 4.3. What is not an exception

- Changing gate/linter configuration **to make a specific PR pass** — prohibited always. A legitimate configuration change exists only as E-D (a change to the standard itself): a separate PR with discussion and the §5 sign-offs — that is an edit of the standard, not an exception.
- Weakening or deleting tests to fit the current code without proof that the test is defective (H5) — not an exception, a violation.
- Faking a verification result (H6) — not an exception, a violation with established consequences (§8).
- Secrets scanners (Q-07): no exceptions; a leak = immediate rotation + history sanitization.
- Manual edits of CI reports, artifact forgery — a violation, not an exception.

### 4.4. Urgent deviations (incidents)

During an active incident, an "act first" deviation is allowed: an anchor + a draft exceptions record in the same PR; full registration and sign-off — within **1 business day**. An unregistered deviation older than 1 business day automatically becomes a red flag (Q-19 cross-checks `EX-…` anchors against the registry).

## 5. Sign-off levels

| Deviation risk | Sign-off | Examples |
|---|---|---|
| Low: local, reversible, no contracts/data | The PR author + reviewer | An E-A linter suppression in a test |
| Medium: affects the reliability/performance of a module | The tech lead of the module's owner | An E-C on B6/G6 for an internal service |
| High: public contracts, data, security, money | The architect + the domain owner | An E-C on E7 (breaking), G-class rules, calculation formulas |
| Gate configurations (changing thresholds/the gate set) | The standard's owner + tech lead | Lowering the Q-05 threshold |

## 6. Changing the standard itself

If a rule is systematically violated with the same justification — that is a signal not to "hand out exceptions" but to examine the rule:

1. Q-19 automatically detects ≥ 3 E-C exceptions of one principle with one cause and creates a task.
2. The standard's owner must open a PR to the standard: clarify applicability, add an explicit conditional rule, or move it to [RECOMMENDED]/[COND].
3. The decision is recorded in `CHANGELOG.md` (the single version history of the standard).

## 7. Visibility and exception metrics

- The repository's `EXCEPTIONS.md` is the only E-C registry; expired exceptions are highlighted by automation (date checking — L4).
- The sign-off cannot be the author of the change — separation of roles is mandatory for the "medium" and "high" levels (see §5).
- Dashboard metrics: the number of active exceptions; the distribution across principles and modules; the closure rate.
- **The health norm:** growth of active exceptions in a module — a red flag for architecture review. A concentration of exceptions of one principle — a candidate for a change to the standard (section 6).
- Suppression counting (E-A) — by gate Q-11; growth beyond the baseline — a signal.
- Metrics are interpreted jointly: "a low share of exception labels at a high number of suppressions" — a red flag, not health (Goodhart's law: a target metric stops measuring what it was introduced for).

## 8. Response to violations (not filed as exceptions)

Exceptions are managed debt; violations without an exception are sabotage of the pipeline. Classification and consequences:

- **Unintentional** (ignorance): review returns the work for rework; a repeat — a signal to update the L1 instructions/training.
- **Systematic** (repeated violations of one type by one subject): a per-subject metric (agent/human); an escalation threshold (default: 3 confirmed violations of domain H per quarter) — demotion of autonomy: for an agent — "draft PR only" mode and a ban on independent merges; for a human — mandatory pair review.
- **Verification faking (H6)** — equated to sabotage: a mandatory retrospective, immediate demotion of autonomy pending investigation, a recurrence metric on the dashboard next to the exception metrics.

Per-subject metrics (the number of PRs, suppressions, guard labels, and repeat violations per period) are aggregated against "salami-slicing" erosion in small portions.
