# PRD.md — Uhakika: Institutional Contract Revenue Assurance

> **Status:** Specification-only. No product functionality implemented yet.
> **Scope note:** This document separates the **V0 hackathon product** from the **long-term company vision**. Do not read long-term items as build commitments.

---

## 1. Problem

Suppliers and contractors selling under complex institutional contracts (governments, utilities, mining, telecom, NGOs, universities, hospitals, large enterprises) routinely **lose or unnecessarily delay contract revenue**. The cause is rarely a single dramatic event. It is usually a **missing or broken paper trail**: an unfiled acceptance certificate, an expired guarantee, a compliance/tax document the buyer asked for but that never got attached, a late invoice, an amendment nobody recorded, or a follow-up that lapsed.

Today these failures are discovered **late and manually**. A finance lead trying to answer *"Why hasn't this invoice been paid?"* must dig across contracts, invoice systems, delivery logs, email threads, and payment portals — often owned by different teams and different systems. The reasoning that connects an unpaid receivable to its true blocker is trapped in people's heads and spreadsheets.

**Core problem statement:** Suppliers cannot quickly see, with evidence, *why* a specific receivable is stuck, *what* is within their control to fix, and *what* action to take next.

---

## 2. Customer, Economic Buyer, User

- **Beachhead customer:** Tanzania public-sector / institutional suppliers and contractors.
- **Economic buyer:** Finance Director / CFO or Contracts/Commercial Manager who owns receivables and cash-flow risk and feels the cost of delayed revenue.
- **Primary user:** Contracts administrator, billing/AR officer, or project/delivery manager who answers "why is this payment stuck?" and prepares follow-ups.
- **Long-term market:** Any company selling under complex contracts to institutional buyers (governments, utilities, mining, telecom, NGOs, universities, hospitals, large enterprises).

*Assumption (to validate):* The economic buyer and day-to-day user may be different people; the buyer cares about cash-flow at risk, the user cares about the specific blocked invoice and next action.

---

## 3. Jobs To Be Done

1. When a receivable is unpaid past expectation, I want to know **exactly what is blocking it, with evidence**, so I can act instead of guessing.
2. I want to separate **what I can fix** from **what is the buyer's problem**, so I don't waste effort or make unfounded claims.
3. I want a **recommended next action** and the ability to **approve consequential actions** (e.g., a formal payment-processing request) before anything is sent.
4. I want to **quantify revenue at risk** so I can prioritize.
5. (Longer term) I want continuous **watchdog** monitoring so blockers are caught before payment terms are breached.

---

## 4. Current Workflow (status quo we replace)

1. Invoice issued → payment due date passes → someone notices non-payment.
2. Human manually checks: Was it delivered? Accepted? Was the invoice on time? Is a guarantee/compliance doc missing? Is the buyer funded?
3. Findings scattered across email, shared drives, ERP, and institutional payment portals.
4. Conclusion and follow-up drafted by hand; often based on incomplete information.

**Pain:** slow, error-prone, non-reproducible, and untraceable. Nobody can show the audit trail that proves *why* a conclusion was reached.

---

## 5. Problem Evidence (why this matters)

*Assumption / to be strengthened with real interviews during the build:* delayed/unclaimed contract revenue is a known, recurring pain in institutional supply chains where payment is gated by documentation and compliance steps. The **hero scenario** in §7 encodes the failure pattern the product must resolve.

> Honesty note: these are framed as problem hypotheses to validate, not proven statistics. Do not insert fabricated numbers into the demo.

---

## 6. Product Promise

Uhakika answers *"Why hasn't this been paid?"* with an **evidence-backed investigation** — not a guess. It forms competing hypotheses, retrieves real evidence through the Zetaris data layer, rejects what the evidence does not support, identifies the strongest supported cause, quantifies the revenue at risk, recommends the next action, and requires human approval before consequential actions — with the full trace shown.

**What Uhakika does NOT promise:** it does **not** "make the government pay you." It surfaces supplier-controllable blockers, execution/documentation risks, and external buyer/payment blockers, grounded in evidence.

---

## 7. Hero Workflow (the demo)

**Demo question:** *"Why hasn't our TZS 126,000,000 invoice been paid?"*

The system must **not jump to an answer.** It runs a disciplined investigation:

1. Understand the request.
2. Create competing investigation hypotheses:
   - **H1** — delivery incomplete
   - **H2** — acceptance missing
   - **H3** — invoice submitted late
   - **H4** — required evidence / compliance document missing
   - **H5** — external buyer / funding / payment-stage blockage
3. Retrieve evidence through **Zetaris**.
4. Evaluate each hypothesis against evidence.
5. Reject unsupported hypotheses.
6. Retry / retrieve more evidence if insufficient.
7. Identify the strongest supported cause.
8. Show evidence and source references.
9. Quantify revenue at risk.
10. Recommend the next action.
11. Require human approval for consequential actions.
12. Record the trace.

**Example final result (canonical demo output):**

```
TZS 126,000,000 AT RISK

Cause:
Required tax/compliance evidence requested by the buyer is missing.

Rejected:
- incomplete delivery
- missing acceptance
- late invoice

Evidence:
- contract clause CLAUSE-7.2
- invoice INV-004
- delivery record DEL-009
- acceptance certificate CERT-018
- communication MSG-037

Recommended action:
Submit missing evidence and issue formal payment-processing request.
```

---

## 8. V0 Scope (hackathon) — IN

- One **hero question** investigated end-to-end (thin slice): invoice → hypotheses → evidence via Zetaris → evaluation → supported cause → revenue-at-risk → recommended action → human approval gate → trace log.
- **Three core named agents doing distinct work** — `InvestigatorAgent`, `EvidenceAgent`, `EvaluatorAgent`. (A separate `ActionAgent` is **STRETCH**; in V0 the recommendation + approval gate is handled by the InvestigatorAgent/orchestrator.) See `ARCHITECTURE.md`.
- A routing **Intent Router** stage — for the **live** path this must be powered by the required Meterless Engine **Scout Intent**; until Scout Intent is wired and verified, a deterministic fallback router is used and clearly labeled `fallback` (**never** presented as Scout Intent). The router is a stage, not one of our core agents.
- Evidence retrieval via **Zetaris REST/SQL** (configured by `ZETARIS_REST_URL` / `ZETARIS_ORG_ID` / `ZETARIS_API_KEY`) over a **synthetic, clearly-marked** dataset backed by **reproducible CSV fixtures**, covering the minimum hero subset (see `DATA_CONTRACT.md` §10: contracts, invoices, deliveries, acceptance_records, communications, **compliance_items**, payment_status).
- **Hypothesis generation + explicit rejection** of unsupported hypotheses (the "explain why" differentiator). H4 must be grounded by `compliance_items`, not inferred from a communication alone.
- **A single programmatic interface for judges: `POST /run`** (see `ARCHITECTURE.md` §10). Extra status/poll/approve/reject endpoints are stretch.
- **One Investigation Workspace + a Trace Panel** (see §11) — not multiple screens.
- **Sample mode** that executes the **real pipeline** (parsing, routing contract, investigation, evidence-retrieval interface, hypothesis evaluation, retry, result and trace construction) over synthetic/cached evidence via a **credential-free local adapter**, and **derives the supported cause at runtime** — it must **never return a stored/pre-written answer** — so the demo is deterministic even if live runtime endpoints are unavailable. Sample mode is **credential-free but, on its own, is NOT sufficient proof** of a Zetaris / Nightshift / Scout Intent / Nemotron integration.
- Meterless Engine **Scout Intent** powering the **live** routing stage (the required Engine) — *only once Nightshift/Engine integration is verified; until then a deterministic `fallback` router is used and the run is clearly labeled sample/fallback, never Scout Intent*.

## 8b. Explicitly OUT of V0 (Non-Goals)

V0 is **NOT**:
- **Tender / bid discovery** software.
- **Generic procurement / e-procurement** software.
- **Generic contract-lifecycle-management (CLM)**.
- **A generic chatbot** (chat without an evidence-backed investigation is out of scope).
- **Accounting / bookkeeping ERP**.
- **Autonomous payment execution** (no actual payment actions, no bank rails, no real buyer integrations).
- Not a multi-currency portfolio dashboard, analytics warehouse, or ML model training.
- No autonomous sending of external communications without human approval.
- No production authentication / multi-tenant SaaS hardening.
- Not claiming features that are unimplemented (Nightshift World Model, direct NVIDIA, Meterless Engine live integration, `POST /run`, etc.).

**STRETCH (deferred, not V0):** `ActionAgent` as a separate agent, guarantees-based workflow, portfolio dashboards, multiple UI pages, real-time streaming, complex authentication, multiple REST endpoints, production-grade infrastructure.

---

## 9. User Stories (V0)

- **US-1** As an AR officer, I ask why a specific invoice is unpaid and receive an evidence-backed cause. *(Accept: the supported cause cites ≥1 evidence ID; unsupported hypotheses are shown rejected.)*
- **US-2** As a contracts manager, I see which blockers are supplier-controllable vs. external. *(Accept: each finding is labeled by blocker class.)*
- **US-3** As a finance lead, I see the revenue at risk quantified for the receivable. *(Accept: amount TZS 126,000,000 shown and tied to the invoice record.)*
- **US-4** As a user, I get a recommended next action. *(Accept: recommendation references the resolved cause.)*
- **US-5** As an approver, I must approve before a consequential action (formal request) is triggered. *(Accept: action stays in "pending approval" until explicit approve; reject path exists.)*
- **US-6** As a reviewer/judge, I can see the operational trace of how the conclusion was reached. *(Accept: trace shows agent, action, query/tool, source summary, decision, confidence, retry count, model route.)*
- **US-7** As a demo operator, I can run in sample mode with deterministic synthetic data. *(Accept: sample mode reproduces the hero result without live runtime.)*

---

## 10. Acceptance Criteria (hero path)

1. A judge can call a single **`POST /run`** with the hero question and receive the canonical result shape (§7): AT RISK amount, supported cause, rejected hypotheses, evidence with IDs, recommendation, trace.
2. Every asserted cause references real evidence IDs from Zetaris; removing that evidence must remove/downgrade the conclusion (anti-fabrication check).
3. H1–H3 are explicitly evaluated and rejected with reasons in the trace; **H4 is selected as strongest supported and grounded by a `compliance_items` row (`required=true`, `submitted=false`)**, citing a `clause_ref` (e.g., `CLAUSE-7.2`) and the supporting `MSG-037`.
4. If evidence is insufficient, the system retrieves more (bounded retry) or reports "insufficient evidence" rather than inventing a cause; **absence must not be inferred merely because no communication mentions an item.**
5. Consequential actions require human approval; the default state is pending-approval, never auto-sent.
6. **Three core named agents** (`InvestigatorAgent`, `EvidenceAgent`, `EvaluatorAgent`) perform distinct, visible work with delegation (≥2 requirement satisfied; `ActionAgent` is stretch).
7. All evidence flows through Zetaris; all product AI runs through Nightshift (or clearly-labeled sample mode when runtime is unavailable). No invented model IDs/endpoints in code — configuration only.
8. **No hardcoded final outputs:** the supported cause/recommendation are derived from evidence at runtime. Golden values in §7 are test fixtures only.
9. **Sample mode executes the real pipeline** and derives the answer at runtime (never a stored reply), using a credential-free adapter over synthetic evidence, and is labeled as synthetic.

---

## 11. Key Screens (V0)

**V0 is a single Investigation Workspace plus a trace panel — not six screens.**

1. **Investigation Workspace (one main view)** containing:
   - question / input (or pick the hero invoice)
   - invoice / receivable context
   - revenue-at-risk amount
   - hypotheses and their statuses (investigating / supported / rejected + reason)
   - supported cause (with blocker class) and rejected causes
   - cited evidence (cards with IDs and source summaries)
   - recommended action
   - human approval control where appropriate
2. **Trace Panel** — chronological operational trace (no chain-of-thought; only actions/evidence/decisions).

*Stretch (not V0): separate pages for Ask / Evidence / Conclusion / Action / Approval; portfolio watchlist; aging dashboard; cross-contract risk heatmap; monitoring/alerts; real-time streaming.*

---

## 12. Product States

- **Idle** — awaiting a question.
- **Investigating** — hypotheses formed, evidence being retrieved. *(Real-time/streamable progress is **stretch/polish only**; V0 may use a simple sequential or single-result update.)*
- **Insufficient Evidence** — needs more retrieval or a human-supplied document; not a final answer.
- **Conclusion Ready** — supported cause + evidence + recommendation, pending human review.
- **Pending Approval** — a consequential action is staged, awaiting explicit approval.
- **Action Approved / Rejected** — recorded with who/when (never auto-executed).
- **Sample Mode** — deterministic run that executes the real pipeline over synthetic evidence and **derives the answer at runtime (never a stored reply)**; clearly labeled as synthetic.
- **Error / Unavailable** — runtime or Zetaris unavailable; show what failed and fall back to sample mode if appropriate.

---

## 13. Failure States (must be handled gracefully)

- Evidence not found → do not fabricate; report gap, optionally request more evidence.
- Ambiguous/conflicting evidence → present competing supported causes with confidence, ask for human disambiguation.
- Zetaris query failure / stale request ID → surface failure; retry with fresh request ID; if persistent, degrade to "cannot retrieve."
- Nightshift/model route unavailable → surface; use sample mode; never claim live reasoning that did not happen.
- All hypotheses rejected (no supported cause) → "no sufficient basis to conclude," list what evidence would resolve it.
- Approval bypass attempt → blocked; consequential actions require the explicit human gate.

---

## 14. Human Approval Points

- Sending/issuing any **formal payment-processing request** or external communication.
- Any action with external effect or that leaves the system boundary.
- Default posture: **system recommends, human approves.** Approve/Reject/Edit are first-class, and recorded in the trace.

---

## 15. Success Metrics

**V0 demo/product metrics:**
- Hero question reaches a correct, evidence-backed conclusion end-to-end (reliable on sample mode).
- 100% of asserted causes cite ≥1 valid evidence ID; 0 fabricated-evidence instances.
- Unsupported hypotheses are explicitly rejected (count shown).
- At least two named agents visibly collaborate.
- Time from question to conclusion (target: fast enough for a live demo, TBD numeric threshold).
- Sponsor-tech coverage: Zetaris used for all evidence; Nightshift primary runtime; ≥1 Meterless Engine feature (once verified).

**Long-term / business metrics (vision, not V0 commitment):**
- Reduction in Days Sales Outstanding (DSO) on monitored receivables.
- Value of previously-blocked revenue recovered / unblocked.
- Blockers caught before payment-terms breach (watchdog hits).
- Supplier-controllable blockers resolved vs. left.

---

## 16. Risks

| Risk | Mitigation |
|---|---|
| Nightshift runtime setup unfinished during build window | Deterministic **sample mode**; keep runtime config-driven, mark `TBD`, do not claim live. |
| Direct NVIDIA/Nemotron blocked for Tanzania | Keep model routing configurable; investigate Nightshift-compatible Nemotron; never hardcode a model ID. |
| Fabricated-evidence temptation in AI output | Anti-fabrication acceptance test; conclusions require evidence IDs; retrieval only via Zetaris. |
| Scope creep toward generic procurement software | Hard non-goals (§8b); protect the thin-slice hero workflow first. |
| Judging favors reliability over breadth | Prioritize Impact/Technical; cut features before cutting reliability of hero path. |
| Zetaris query correctness / request-ID reuse | Fresh request ID per query; one SQL statement per call; smoke tests per query change. |

---

## 17. Assumptions (to validate)

- Synthetic data can realistically represent institutional contract/payment documentation flows for the hero scenario.
- The demo can run convincingly in sample mode even if a live runtime is only partially available.
- Buyer-side blockers (H5) can be represented in data as status fields without implying real integrations.
- The true blocker in the hero dataset is the missing compliance/tax evidence (H4), matching the canonical output in §7.

> Any change to these assumptions during the build should be logged in `BUILD_LOG.md`.

---

## 18. Future Roadmap (long-term vision — NOT V0)

- Continuous watchdog monitoring with alerts before terms are breached.
- Portfolio-level revenue-at-risk dashboards and aging across many contracts.
- Broader document/compliance coverage (guarantees/securities lifecycle, amendments).
- Real buyer-portal/institutional integrations (where APIs exist) and richer payment-status ingestion.
- Meterless **World Model** for scenario simulation ("if we submit this evidence, expected effect on timeline").
- Multi-market expansion beyond Tanzania; localization of compliance rules per buyer type.
- Audit-ready evidence chains and regulatory-grade traceability.

**V0 vs. Vision discipline:** everything above is explicitly future/long-term. Only §8 (V0 Scope) is buildable during the hackathon.
