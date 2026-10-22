# AGENTS.md — Operating Manual for AI Coding Agents

> **Status:** Specification-only. No product functionality is implemented yet.
> **Read this file first, then `PRD.md`, `ARCHITECTURE.md`, `DATA_CONTRACT.md`, and `BUILD_PLAN.md`, before touching any code.**

This document is the **binding rulebook** for every AI coding agent (Qoder/Qwen or any other assistant) working in this repository. It exists so that implementation stays consistent, safe, and aligned with hackathon judging, even across multiple agents and teammates.

When a rule here conflicts with a chat instruction, **the rule wins unless a human explicitly overrides it in writing.** When two rules conflict, security rules outrank all others.

---

## 1. Project Mission

**Team:** Uhakika Labs
**Hackathon:** Open Agent Hackathon 2026
**Primary track:** Track 2 — *The Agent That Can Explain Why*
**Secondary architectural strength:** Track 1-style fragmented-data reasoning
**Product category:** Institutional Contract Revenue Assurance
**Beachhead:** Tanzania public-sector / institutional suppliers and contractors.

**Core promise (verbatim intent):**
We help suppliers avoid losing or unnecessarily delaying contract revenue because a contractual obligation, document, acceptance record, guarantee, amendment, invoice, or follow-up was missed — and we **explain exactly what is blocking each receivable**, with evidence.

**Long-term market:** Companies selling under complex contracts to governments, utilities, mining companies, telecom companies, NGOs, universities, hospitals, and large enterprises.

### Non-negotiable product honesty rules
- **NEVER claim:** "We make the government pay you." The product does not force payment.
- The product identifies three distinct blocker classes:
  1. **Supplier-controllable blockers** (documents/evidence/actions the supplier can fix).
  2. **Execution/documentation risks** (delivery, acceptance, guarantees, compliance).
  3. **External buyer/funding/payment-stage blockages** (outside supplier control).
- Every conclusion must be **evidence-backed and traceable** to source records. Do not assert a cause without citing evidence IDs.
- **Never fabricate evidence at runtime.** If evidence is missing, say so and retrieve more or escalate — do not invent it.

---

## 2. Non-Negotiable Architecture Rules

1. **Zetaris is the mandatory data layer.** All core business evidence (contracts, invoices, deliveries, acceptance, correspondence, guarantees, payment status) must be retrieved **through Zetaris**. Never bypass Zetaris to reach an ad-hoc data source for business evidence.
2. **Meterless Nightshift is the product AI runtime/provider.** Never bypass Nightshift for the production AI runtime. Qoder/Qwen are **build-time tooling only** and must not become the product runtime.
3. **Nemotron routing is configurable.** Do **not** hardcode or invent a Nemotron model ID, provider, or runtime URL. Model/provider routing must remain configurable through environment variables supplied later.
4. **At least two named agents must perform distinct work.** The final system must visibly demonstrate: delegation, evidence retrieval, critique, retry/branching, tool use, grounded conclusions, and trace logs.
5. **No giant, unapproved changes.** Prefer small, reversible commits. Do not refactor or rewrite large amounts of code without explicit human approval.
6. **Undecided components are marked `TBD`.** Do not claim a technology/component is used unless it is installed, configured, and verified. Never assert unimplemented features as working.
7. **Three core agents only in V0.** The V0 uses `InvestigatorAgent`, `EvidenceAgent`, `EvaluatorAgent`. `ActionAgent` is **STRETCH** — in V0 the recommendation + human-approval gate is handled by the `InvestigatorAgent`/orchestrator. The **Intent Router is NOT one of our agents** — it is a routing stage optionally powered by the **Meterless Engine "Scout Intent"** (a candidate, `TBD`). Only Scout Intent / World Model may be called "Meterless Engines"; never label our agents or the Intent Router as Meterless Engines.
8. **Never hardcode final conclusions.** Golden/canonical outputs (e.g., the PRD §7 result) are **test fixtures only**. The supported cause, rejected hypotheses, revenue-at-risk, and recommendation must be **derived from evidence at runtime** on every run — in live mode AND in sample mode. `SAMPLE_MODE` must never return a stored/pre-written answer.

Target agent pipeline — **LOCKED V0** (direction, not yet built — see `ARCHITECTURE.md`):

```
User
→ POST /run
→ Intent Router   (routing stage; optionally powered by Meterless Engine "Scout Intent" — TBD. NOT a core agent)
→ InvestigatorAgent   (frames case, generates hypotheses, orchestrates + holds shared case state + approval gate)
→ EvidenceAgent       (Zetaris-only retrieval)
→ Zetaris
→ EvaluatorAgent      (scores/rejects; bounded retry / additional retrieval)
→ supported conclusion
→ recommendation + human approval gate
→ visible operational trace
```

`ActionAgent` and a separate follow-up/verification stage are **STRETCH** for V0.

---

## 3. Security Rules (highest priority)

- **Never print, log, commit, or expose credentials** or secret values. This includes API keys, tokens, and connection strings.
- **`.env` is sacred and Git-ignored.** Never `git add -f .env`. Never force-add ignored files.
- Secrets live only in `.env` (local) / the deployment secret store (later). Refer to them in code **only by variable name**, never by value, and never inline a literal secret.
- Do not paste real credential values into docs, commits, logs, trace outputs, demo slides, or chat responses.
- Logs must contain **operational traces only** (see §9), never secrets or raw sensitive payloads.
- Do not transmit real customer data to external services without an explicit, approved decision.
- **No NVIDIA / Nightshift provider credential may ever enter project files**, docs, config, config templates, or `.env.example` (placeholders only there).
- **Demo/screenshots must hide all credentials.** Mask or crop any key material before capture.
- **Never give build tooling (Qoder/Qwen) the product's NVIDIA/Nightshift provider credentials.** Those secrets belong only to the product runtime and its environment.

Current environment variable **names** (values are intentionally not recorded here): `METERLESS_BASE_URL`, `METERLESS_API_KEY`, `NEMOTRON_MODEL`. Any additional Meterless/Nightshift variables will be supplied later via `.env` — do not invent their values.

---

## 4. Sponsor / Technical Rules

- **Zetaris:** data layer is mandatory and currently running locally, verified 9/9.
  - Use the **REST API** for the application. Expected REST base URL: `http://localhost:8888/api/v1.0`.
  - SQL endpoint pattern: `/sql-editor/sqls/run`.
  - **Every query must use a fresh request ID.** Reusing a request ID is a bug.
  - **Lightning SQL rules apply.** **One SQL statement per call** — never batch multiple statements in a single call.
  - Never print credentials.
- **Meterless Nightshift:** must be the primary AI runtime/provider. Setup is **still in progress**. Do **not** invent the final Runtime URL or token; they arrive via environment variables later. Mark runtime integration `TBD` until verified.
- **Meterless Engine:** at least one Engine must power a real feature. Likely first candidate: **Scout Intent**; possible later candidate: **World Model**. **Do not claim either is implemented yet.**
- **NVIDIA / Nemotron:** desired reasoning model. Direct NVIDIA verification is currently problematic for Tanzania. Alternative Nightshift-compatible Nemotron routing is under investigation. Do not hardcode or invent a model ID; keep routing configurable.
- **Coding environment:** Qoder IDE with a Qwen model assisting development. **Cursor is optional. Qoder is an allowed coding tool.** **Qwen/Qoder is BUILD tooling only** and does **NOT** replace the product runtime. The product runtime must remain Meterless Nightshift. Never pass NVIDIA/Nightshift provider credentials to build tooling.

---

## 5. Data Rules

- The demo uses **synthetic but realistic** datasets. **Synthetic demo data must be clearly marked as synthetic.**
- Every important conclusion must be traceable to **evidence IDs** (e.g., `INV-004`, `DEL-009`, `CERT-018`, `MSG-037`). See `DATA_CONTRACT.md`.
- **Never fabricate evidence at runtime.** Retrieval must come from Zetaris datasets. If data is absent, the correct behavior is "insufficient evidence → retrieve more / escalate / stop," not invent.
- Core sources for the **hero thin slice** (see `DATA_CONTRACT.md` §10): Contracts, Invoices, Deliveries, Acceptance/certification, Correspondence, **Compliance items (required/submitted supporting documents)**, Payment status. **Guarantees/securities are STRETCH** and must not be required by the hero workflow.
- **H4 (missing compliance/tax evidence) must be grounded by `compliance_items`** (`required = true`, `submitted = false`), not by a communication alone. Communications **support** H4/H5 but are **not proof of non-submission**, and absence must never be inferred merely because no communication mentions an item.
- Identifier fields to preserve for traceability: `contract_id`, `invoice_id`, `delivery_id`, `certificate_id`, `message_id`, `item_id` (compliance), `payment_id`, and a stable `clause_ref` (e.g., `CLAUSE-7.2`) so a cited contract clause is traceable.

---

## 6. SQL Rules (Zetaris / Lightning SQL)

- **One SQL statement per API call.** Do not concatenate statements with semicolons for execution.
- **A fresh request ID per query.** Generate a new unique ID for every call.
- Follow **Lightning SQL** syntax/rules; do not assume full ANSI/Postgres feature availability unless verified.
- Prefer explicit column lists over `SELECT *` for evidence queries so outputs are stable and readable.
- Parameterize/validate identifiers; never interpolate untrusted strings into SQL.
- Keep queries read-focused for evidence gathering. Do not perform writes/mutations as part of investigation unless an approved phase explicitly requires it.
- Test every query against the local Zetaris instance and confirm the request ID is fresh and the result is grounded in a real dataset.

---

## 7. Git Rules

- Branch: **`main`**. Baseline commit: `chore: capture pre-build scaffold and git setup` (records the empty pre-build scaffold).
- **Never force-add `.env`** or any ignored file. `.env` and `.venv/` are ignored.
- Prefer **small, reversible commits** with conventional messages (`chore:`, `feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- Do not commit until a human reviews. Until told otherwise, produce changes and show `git status` / diffs, then **stop and wait for approval to commit.**
- Never rewrite published history (no force-push, no destructive resets) unless a human explicitly requests it.
- One logical task / one logical commit per change. Avoid mixing unrelated edits into one commit.

---

## 8. Coding Standards

- **Do not create Python code, frontend code, or implement APIs** during the documentation/setup phase. Code begins only when an approved phase in `BUILD_PLAN.md` says so.
- Follow the folder structure in `ARCHITECTURE.md` §Likely Folder Structure. Keep responsibilities separated per agent/module.
- Write functions with a single clear responsibility; name things after the domain (`EvidenceAgent`, `hypothesis`, `receivable`), not generic placeholders.
- Handle errors explicitly (network, Zetaris request failures, empty results, model unavailability). No silent failures. A failed retrieval must surface as "evidence not obtained," never as a fabricated result.
- Keep configuration in environment variables and a single config module; do not scatter literals. Never inline secrets or model IDs.
- Add type hints where practical and docstrings for public functions. Match any style the existing (empty) stubs and teammates converge on.
- Do not add dependencies/packages unless a phase explicitly approves them. **No package installs during setup.**
- Comments explain *why*, not *what*. No dead code, no placeholder "TODO-forever."
- Keep prompts (if used) in `prompts/` rather than embedded as sprawling inline strings once implementation starts.

---

## 9. Logging / Trace Rules

- **Do not create fake chain-of-thought logs.** Never expose or manufacture private reasoning.
- Logs contain **operational traces only**, with these fields (see `ARCHITECTURE.md` §Traces for format):
  - `agent` (name)
  - `action`
  - `query` / `tool` used
  - `source` / result summary
  - `decision` status
  - `confidence`
  - `retry_count`
  - `model_route` used (name/route as configured, never invented)
- Every conclusion written to a trace must reference the **evidence IDs** it is based on and the hypotheses considered/rejected.
- Logs must never contain credentials or secret values.

---

## 10. Testing Expectations

- Every phase in `BUILD_PLAN.md` has defined **exit criteria** and a **test**. A task is not done until its test passes and is reported.
- Maintain `smoke_test.py` as the end-to-end wiring check once implementation starts (currently an empty placeholder — do not implement now).
- Zetaris connectivity is considered **verified 9/9** locally; re-run connectivity/query checks when the data layer changes.
- Prefer an **end-to-end thin slice** (one invoice question → evidence → conclusion → recommendation → trace) early, then broaden.
- Test evidence-based reasoning explicitly: a conclusion must fail its test if evidence is removed (guards against fabrication).
- Golden/canonical results are compared against **runtime-derived** output; never ship a hardcoded answer to satisfy a test.
- The judge-facing programmatic interface is a **single `POST /run`** (planned). Avoid extra status/poll/approve/reject REST endpoints in V0 — those are stretch.
- Record test results in `BUILD_LOG.md`.

---

## 11. Definition of Done (DoD)

A change is "done" only when **all** are true:
1. It matches the mission, hero workflow, and track goal ("explain why").
2. It respects every rule in §2–§9 (Zetaris for evidence, Nightshift for runtime, no invented endpoints/models/credentials, no bypasses, no fabricated evidence).
3. Claims are supported by evidence IDs and are marked synthetic where applicable; unimplemented features are not claimed as working.
4. Relevant test from the phase passes; failures are handled explicitly.
5. Operational trace is produced/present.
6. Diff is small, reviewable, and reversible; `git status` shows no ignored/secret files staged.
7. `BUILD_LOG.md` records what happened.
8. A human has reviewed and approved before commit/submission claims.

---

## 12. Mandatory Agent Workflow

Follow this loop for **every** task, in order. Do not skip steps. Explain before changing. **One task at a time.**

```
READ → PLAN → EXPLAIN → CHANGE → TEST → REPORT → WAIT FOR APPROVAL
```

1. **READ** — Read `AGENTS.md`, `PRD.md`, `ARCHITECTURE.md`, `DATA_CONTRACT.md`, and the relevant phase in `BUILD_PLAN.md`. Inspect current files before proposing changes.
2. **PLAN** — Define the smallest reversible step that advances one acceptance criterion / phase. List files to touch. Identify open `TBD`s and blocking questions.
3. **EXPLAIN** — Before modifying anything, tell the human: what you will change, why, the risks, and what you will **not** touch. (This "explain before changing" rule is mandatory.)
4. **CHANGE** — Make the minimal edit. Stay within scope. No installs, no secrets, no invented endpoints/models, no giant rewrites, no out-of-phase features.
5. **TEST** — Run the phase's test / smoke checks; verify evidence-based behavior. Report pass/fail honestly.
6. **REPORT** — Summarize what changed, files touched, test results, and update `BUILD_LOG.md`. Show `git status`/diff.
7. **WAIT FOR APPROVAL** — Stop. Do not commit or start the next task until the human approves. Never proceed on assumption.

### Behavioral rules baked into the workflow
- **Explain before changing** — never edit silently.
- **One task at a time** — no parallel feature work across phases.
- **Never invent APIs / models / endpoints** — leave `TBD` and ask.
- **Never expose credentials** — mask values; reference names only.
- **Never bypass Zetaris for core business evidence.**
- **Never bypass Nightshift for the production AI runtime.**
- **Never silently change product scope** — propose the change and wait for approval.
- **Never replace required sponsor technologies** (Zetaris, Nightshift, Meterless Engine) with substitutes.
- **Never hardcode final conclusions** — derive from evidence at runtime; canonical values are test fixtures only.
- **No giant changes without approval.** **Do not make unrelated changes.**
- **Prefer the smallest working implementation** and small, reversible commits.
- **Keep documentation synchronized** when architecture or data contracts change (update the affected spec files in the same task).
- **If project documents conflict, STOP and report the conflict** rather than guessing.
- **Report all files changed**, then **stop after the requested task** and wait for approval.

---

## 13. Judging-Aware Priorities

Hackathon scoring: Impact 30 · Technical 20 · Innovation 15 · Demo 15 · Product & UX 10 · Sponsor Tech 10.
Optimize in this order:
1. Real problem and clear impact
2. A working, reliable agent
3. Evidence-backed reasoning
4. Strong demo
5. Good UX
6. Additional features **last**

When in doubt about scope, cut features and protect the reliable, evidence-backed hero workflow.
