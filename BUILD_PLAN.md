# BUILD_PLAN.md — Uhakika Implementation Plan

> **Status:** Planning only. No product code implemented yet. Plan covers the remaining Open Agent Hackathon 2026 build window through submission.

---

## 1. Team & Roles (provisional)

> **Provisional until confirmed.** Re-confirm owners before Phase 2 starts.

| Person | Provisional role | Primary focus |
|---|---|---|
| **Ali** | Product owner | AI/data, final integration, sponsor technology, architecture understanding |
| **Friend 1** | Frontend / UI / UX | Investigation UI, evidence cards, approval gate, trace view |
| **Friend 2** | Backend / integrations / testing | Agent orchestration, Zetaris client, Nightshift client, tests |

---

## 2. Prioritization (from judging weights)

Impact 30 · Technical 20 · Innovation 15 · Demo 15 · Product & UX 10 · Sponsor Tech 10.
Optimize in order: **real problem/impact → working reliable agent → evidence-backed reasoning → strong demo → UX → extras.**

**Guiding principle: build an end-to-end thin slice early.** Get one invoice question flowing through hypotheses → evidence → conclusion → recommendation → approval → trace before broadening scope. A reliable thin slice beats a broken wide build.

```
Phase 0 → 1 → 2 → 3 → 4(thin slice)→ 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14
                        └────────────── thin slice complete here ┘
```

---

## 3. Phases

### Phase 0 — Environment / Setup
- **Owner:** Ali (with Friend 2 support)
- **Scope:** Git repo (done), `.env` handling, `.venv`, Zetaris local verification, Nightshift install in progress, sponsor accounts.
- **Dependencies:** none
- **Exit criteria:** Zetaris running locally verified 9/9; `.env`/`.venv` ignored; branch `main`; baseline commit present. Nightshift install status recorded (may still be in progress).
- **Test:** `git check-ignore .env .venv` passes; Zetaris 9/9 check re-run.
- **Risks:** Nightshift/runtime not ready → mitigated by proceeding to docs and sample mode; never invent runtime values.
- **Status:** Largely complete (see `BUILD_LOG.md`).

### Phase 1 — Documentation / Specification  ← **current phase**
- **Owner:** Ali
- **Scope:** The six spec files (AGENTS/PRD/ARCHITECTURE/DATA_CONTRACT/BUILD_PLAN/BUILD_LOG). No code.
- **Dependencies:** Phase 0
- **Exit criteria:** six docs reviewed & approved; every `TBD` explicit; no invented endpoints/models/credentials.
- **Test:** human review against AGENTS rules (walkthrough).
- **Risks:** spec drift → keep decisions logged; revisit docs as `TBD`s resolve.

### Phase 2 — Sponsor Smoke Tests
- **Owner:** Friend 2 (Ali reviews sponsor compliance)
- **Scope:** Standalone smoke checks: (a) Zetaris REST/SQL call returns rows with a **fresh request ID**, one statement per call; (b) minimal Nightshift round-trip **once runtime env vars are provided** — else clearly `TBD`/deferred, no fakes.
- **Dependencies:** Phase 1; Nightshift env vars for (b)
- **Exit criteria:** Zetaris query proven end-to-end; Nightshift either proven or explicitly deferred to sample mode with a logged reason.
- **Test:** `smoke_test.py` runs the checks; prints pass/fail; **never prints credentials**.
- **Risks:** runtime unavailable → do not claim live; gate later phases on sample mode.

### Phase 3 — Data Layer (synthetic seed + Zetaris wiring)
- **Owner:** Ali (data) + Friend 2 (Zetaris client)
- **Scope:** Seed the **hero minimum subset** from `DATA_CONTRACT.md` §10 (contracts, invoices, deliveries, acceptance_records, communications, **compliance_items**, payment_status; **guarantees are STRETCH**). Implement EvidenceAgent's Zetaris query helpers.
- **Dependencies:** Phase 2
- **Exit criteria:** each dataset queryable via Zetaris returning the canonical IDs (INV-004, DEL-009, CERT-018, MSG-037, **CMP-005**, PAY-011, CTR-001 with `clause_ref`); synthetic markers present; validation rules (§9) pass.
- **Test:** query each table; assert hero rows exist and FK integrity holds; assert `compliance_items` contains a `required=true, submitted=false` row (H4 groundable without relying on communications).
- **Risks:** schema mismatch with Lightning SQL → validate dialect early; accidental fabrication temptation → enforce read-only, evidence-by-ID only.

### Phase 4 — Core Investigation Loop (THIN SLICE)
- **Owner:** Ali (agents) + Friend 2 (orchestration)
- **Scope:** Three **core** agents — `InvestigatorAgent` (generates H1–H5, holds shared case state, orchestrates), `EvidenceAgent` (Zetaris retrieval), `EvaluatorAgent` (supported/rejected). `ActionAgent` is **STRETCH** — the recommendation + approval gate live in the InvestigatorAgent for V0. Wrap the loop behind a single judge-facing **`POST /run`** (in-memory/CLI first; `main.py`), **single invoice, sample mode allowed**. Conclusions are **derived from evidence at runtime — never hardcoded**.
- **Dependencies:** Phase 3
- **Exit criteria:** end-to-end via `POST /run`: "Why is INV-004 unpaid?" → revenue at risk = TZS 126,000,000, supported cause = missing compliance evidence (**H4, grounded by `compliance_items` CMP-005 `required=true, submitted=false`, citing `CLAUSE-7.2`**), H1–H3 rejected with evidence-based reasons.
- **Test:** golden test compares **runtime-derived** output to the canonical shape (fixture, not shipped answer); **anti-fabrication test** (remove CMP-005 or flip `submitted=true` → conclusion must change; removing MSG-037 alone must NOT by itself prove/disprove H4).
- **Risks:** jumping to answer / hardcoding → enforce hypothesis-then-evidence order and runtime derivation; keep Nightshift reasoning `TBD` (credential-free adapter) until runtime verified.

### Phase 5 — Evaluator / Critic
- **Owner:** Ali
- **Scope:** Flesh out EvaluatorAgent: score each hypothesis, explicit rejection reasons, **insufficiency detection + bounded retry loop** requesting more evidence.
- **Dependencies:** Phase 4
- **Exit criteria:** system requests more evidence when insufficient instead of guessing; retry_count recorded; max-retry respected.
- **Test:** scenario with partial evidence triggers exactly one bounded re-retrieval then a valid terminal state.
- **Risks:** infinite loops → hard max-retry constant (config).

### Phase 6 — Meterless Engine Integration
- **Owner:** Ali (sponsor tech)
- **Scope:** Wire **Scout Intent** (a **Meterless Engine**, powering the routing **stage** — not a core agent) for the hero intent, if/when integrated; otherwise use a clearly-labeled deterministic fallback router. **World Model** deferred (out of V0). **Do not claim an Engine is live until verified.**
- **Dependencies:** Phase 2 (runtime), Phase 4
- **Exit criteria:** at least one real feature visibly powered by a Meterless Engine, OR documented fallback if Engine unavailable (honestly labeled).
- **Test:** Scout Intent correctly classifies the hero intent vs. a non-matching query.
- **Risks:** Engine availability → keep configurable; if unavailable, mark `TBD` and do not fake it.

### Phase 7 — UI
- **Owner:** Friend 1
- **Scope:** **ONE main Investigation View + a Trace Panel** (not multiple pages). The view shows: question/input, invoice/receivable context, revenue-at-risk, hypotheses + statuses, supported cause + rejected causes, cited evidence (IDs), recommended action, and the human-approval control. It consumes the single `POST /run` interface. Extra pages (separate Ask/Evidence/Conclusion/Action screens, dashboards) are **STRETCH**.
- **Dependencies:** Phase 4 (`POST /run` shapes)
- **Exit criteria:** demo flow clickable end-to-end in sample mode against `POST /run`; synthetic/sample mode visibly labeled.
- **Test:** manual demo walkthrough + basic smoke of the view's data binding.
- **Risks:** frontend talking directly to Zetaris/runtime → forbidden; enforce boundary.

### Phase 8 — Trace / Logging
- **Owner:** Friend 2
- **Scope:** Operational trace store + per-step entries (agent, action, query/tool, source summary, decision, confidence, retry_count, model_route, evidence_ids). **No chain-of-thought.** Expose trace to UI (Phase 7).
- **Dependencies:** Phase 4–5
- **Exit criteria:** every hero run produces a readable trace citing evidence IDs; no secrets in trace.
- **Test:** assert trace has required fields; assert no credential strings appear.
- **Risks:** fabricated/`pretty` logs → logs must reflect real executed steps only.

### Phase 9 — Sample Mode (hardening for demo)
- **Owner:** Ali + Friend 2
- **Scope:** Deterministic, clearly-labeled synthetic run that **executes the same real pipeline** (parsing, routing contract, investigation, evidence-retrieval interface, hypothesis evaluation, retry, result + trace construction) over synthetic/cached evidence via a **credential-free local adapter**, and **derives the answer at runtime** — it **never returns a stored/pre-written result**. Graceful-degrade path when runtime/Zetaris unavailable.
- **Dependencies:** Phase 3–8
- **Exit criteria:** sample mode reproduces the hero output shape reliably and is labeled; supported cause is computed from evidence each run; live mode used when available.
- **Test:** repeated sample runs are deterministic **yet** flipping the `compliance_items` row changes the outcome (proves derivation, not a canned answer); live→sample fallback triggers on simulated runtime outage.
- **Risks:** confusing sample with live → persistent UI label; never claim live reasoning that didn't run.

### Phase 10 — Testing
- **Owner:** Friend 2 (with Ali on reasoning tests)
- **Scope:** Smoke suite, evidence-grounding/anti-fabrication tests, hypothesis-evaluation tests, approval-gate tests, boundary checks (Zetaris-only evidence, Nightshift-only runtime), **and a `POST /run` contract test** (request/response shape) plus a **no-hardcoded-output test** (result must change with evidence).
- **Dependencies:** Phase 4–9
- **Exit criteria:** green suite covering hero path + key failure states + the `POST /run` interface; regressions tracked.
- **Test:** the suite itself; plus a manual judge-style demo run.
- **Risks:** time crunch → prioritize hero-path tests first.

### Phase 11 — README
- **Owner:** Ali
- **Scope:** Quickstart (env setup from `.env.example`, run smoke test, run sample mode, call `POST /run`), architecture summary, sponsor-tech notes, demo script pointer. Also create the submission artifacts: **`README.md`, `.env.example` (placeholders only — no secrets), `input_examples/`, `output_examples/`, and `logs/` (a sample operational trace)**.
- **Dependencies:** Phase 1–10
- **Exit criteria:** a new teammate can clone, install from an approved requirements list (only after a phase permits installs), copy `.env.example`→`.env`, and run the demo; input/output examples and a sample log are present.
- **Test:** clean-clone dry run starts sample mode.
- **Risks:** missing steps → validate via Phase 13.

### Phase 12 — Demo / Deck
- **Owner:** Ali (narrative) + Friend 1 (UI for demo)
- **Scope:** Live demo script around the hero question; slide deck covering problem, impact, evidence-backed reasoning, architecture, sponsor tech, trace proof.
- **Dependencies:** Phase 7–9
- **Exit criteria:** rehearsed ≤ time limit; every claim supported by what actually runs.
- **Test:** dry-run demo on a fresh machine in sample mode.
- **Risks:** overclaiming → strictly avoid "we make government pay"; show rejected hypotheses + trace.

### Phase 13 — Clean-Clone Validation
- **Owner:** Friend 2
- **Scope:** Clone repo to a clean machine, install permitted deps, copy `.env.example`→`.env` and fill values locally (no secrets committed), run smoke test + sample demo via `POST /run`.
- **Dependencies:** Phase 11
- **Exit criteria:** works from scratch; `.env`/`.venv` correctly ignored; no committed secrets.
- **Test:** automated smoke passes on clean clone; manual demo check.
- **Risks:** local-only assumptions → catch missing files/config here, not at submission.

### Phase 14 — Submission
- **Owner:** Ali
- **Scope:** Final repo tidy, tags, submission artifacts (README, deck, demo link/video), sponsor-requirement checklist.
- **Dependencies:** Phase 13
- **Exit criteria:** all submission requirements met and reviewed.
- **Test:** pre-submission checklist signed off by all three.
- **Risks:** last-minute breakage → freeze code before submission; only doc-level edits in freeze.

---

## 4. Thin-Slice Emphasis

The first working end-to-end path (Phase 4) must exist before UI polish (Phase 7) or breadth. By the end of Phase 5 we should demo, through **`POST /run`**: question → routing stage → hypotheses → Zetaris evidence → evaluation → supported cause + rejected H1–H3 → revenue at risk → recommendation → approval gate → trace. The three core agents (`InvestigatorAgent`, `EvidenceAgent`, `EvaluatorAgent`) do this work; conclusions are **derived at runtime**, not hardcoded. Everything after refines and surfaces that single slice.

---

## 5. Cross-Cutting Rules for All Phases

- No installs / no frontend / no databases / no API implementation during Phase 0–1 (setup+docs). Code begins at Phase 2 tests onward, per `AGENTS.md` §8.
- Zetaris for all business evidence; Nightshift for all product AI runtime; model routing configurable; never invent IDs/endpoints/credentials.
- Small, reversible commits; human approval before commit; explain-before-change.
- Update `BUILD_LOG.md` every phase; keep `TBD`s honest and current.
- Re-validate this plan after each phase; adjust owners/sequence only with a logged decision.

---

## 6. Provisional Milestones (relative — no dates invented)

1. **Spec approved** (end Phase 1) — now.
2. **Data + smoke verified** (end Phase 3).
3. **Thin slice works** (end Phase 5) — highest-value checkpoint.
4. **Sponsor tech wired** (Phase 6) + **UI clickable** (Phase 7).
5. **Demo-ready** (Phases 9–12).
6. **Validated & submitted** (Phases 13–14).

Exact calendar scheduling is `TBD` (depends on build-window time remaining and Nightshift readiness).

---

## 7. Submission Artifacts (required, produced in Phases 11 & 13)

The repository must eventually contain:
- **`README.md`** — quickstart, architecture summary, sponsor-tech notes, how to run sample mode and call `POST /run`, demo pointer.
- **`.env.example`** — **placeholders only, never real secrets**; lists required variable **names** (e.g., `METERLESS_BASE_URL`, `METERLESS_API_KEY`, `NEMOTRON_MODEL`, Zetaris base URL, mode flag). No NVIDIA/Nightshift provider credential values are ever committed.
- **`input_examples/`** — sample `POST /run` request payloads (including the hero question).
- **`output_examples/`** — sample `POST /run` responses (labeled synthetic/sample where applicable).
- **`logs/`** — a sample **operational trace** (no chain-of-thought, no secrets).
- **Clean-clone validation** — the whole thing runs from a fresh clone (Phase 13).

---

## 8. Stretch / Deferred (do NOT build unless the thin slice is solid)

To keep V0 buildable by three students, the following are explicitly **STRETCH** and out of the critical path: `ActionAgent` as a separate agent, the guarantees-based workflow, portfolio dashboards, multiple UI pages, real-time streaming, complex authentication, multiple REST endpoints (only `POST /run` is required), and production-grade infrastructure. Defer anything not needed for: question → hypothesis → evidence → evaluation → retry/branch → conclusion → recommendation → trace.
