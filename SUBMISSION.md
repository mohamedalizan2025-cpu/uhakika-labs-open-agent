# SUBMISSION.md — Hackathon Submission Pack (prepared, **not** submitted)

> This file **prepares** the Open Agent Hackathon 2026 / Track 2 submission. It
> does **not** create the HackOS submission, alter the team roster, upload any
> video, publish any deck, or claim an integration that is not proven. Those are
> the human steps listed in §7.

---

## 1. One-paragraph pitch

Uhakika is an explainability-first agent for Tanzanian institutional suppliers
whose earned revenue is stuck in approval pipelines. Given one question — *"why
hasn't this invoice been paid?"* — it retrieves contract, delivery, acceptance,
compliance, communication and payment evidence through **Zetaris**, runs a
rule-grounded evaluator over five explicit hypotheses, and returns the single
supported root cause, the revenue at risk, the rejected alternatives with their
disproof, and an audit-ready trace — with a human approving any action. It is a
reliable thin slice that **proves the cause**, not a wide demo that guesses.

---

## 2. Live demo script (≈4 minutes)

Runbook against the sample-mode stack (see `SETUP.md`):

1. **Frame (20s).** Open the workspace (`http://localhost:5173`). Point out the
   service badge shows **Sample mode** and the header shows `model_route: none`
   in the trace — honest about the current runtime.
2. **Hero (90s).** Ask *"Why hasn't our TZS 126,000,000 invoice been paid?"* for
   `INV-004`. Walk the result top-to-bottom: revenue at risk → supported cause
   **H4** → blocker class `execution_documentation` → the **rejected** H1/H2/H3
   with their disproof → the cited evidence **CMP-005** + the contract tax clause
   (MSG-037 shown as corroboration only).
3. **Anti-fabrication beat (40s).** State that if `CMP-005` were removed, H4
   drops to *insufficient evidence* — the agent will not assert a cause it cannot
   ground. (This is covered by a test; demonstrate verbally or point to the test.)
4. **Breadth (40s).** Run `INV-005` (→ H1, supplier-controllable, TZS 45M) and
   `INV-006` (→ H5, external payment blockage, TZS 75M) to show it is not a
   single hard-coded answer.
5. **Explainability (30s).** Expand the **Trace Panel** — operational actions and
   decisions, retry counts, cited evidence IDs; **no** chain-of-thought, **no**
   secrets. Click **Approve** and note it is a local, explain-only acknowledgement
   (ActionAgent is a deferred stretch).
6. **Close (20s).** Sponsor boundaries: all business evidence via Zetaris; all
   product AI via Nightshift; the live path is honestly gated (see §5).

**Backup if the UI is unavailable:** `POST /run` directly, or the committed
`output_examples/INV-004.json` … `INV-006.json`.

---

## 3. Slide-deck outline (7 slides)

1. **Title** — Uhakika Labs · Track 2 · one-line pitch · team.
2. **Problem & impact** — suppliers waiting on earned revenue; blocker hidden
   across 6 systems; judging weight Impact (30).
3. **The one question, the one answer** — hero `INV-004` result screenshot.
4. **Why you can trust it** — hypothesis board, rejected causes with disproof,
   cited evidence, anti-fabrication (remove CMP-005 ⇒ insufficient).
5. **Architecture** — the Mermaid flow from `README.md` §3 (3 agents + router,
   one `POST /run`, Zetaris data layer, Nightshift live path gated).
6. **Sponsor technology** — Zetaris (live), Nightshift/Nemotron/Scout Intent
   (runtime, gated); what is proven now vs. what the live phase will prove.
7. **Status & roadmap** — thin slice solid; Phase 6 secrets pending; deferred
   ActionAgent/World Model; clean reproducibility (CI, tests, artifacts).

---

## 4. Screenshots plan

| # | Shot | Source |
|---|------|--------|
| 1 | Workspace, empty + service badge "Sample mode" | `http://localhost:5173` before a run |
| 2 | Hero result `INV-004` — revenue + H4 supported + H1/H2/H3 rejected | after run |
| 3 | Evidence panel — CMP-005 + contract clause cited | hero result |
| 4 | Trace panel expanded — actions, retries, `model_route: none` | hero result |
| 5 | `INV-005` and `INV-006` results side by side (breadth) | two runs |
| 6 | CI green on `main` + `pytest` 68-passed terminal | GitHub / local |

---

## 5. Sponsor-tech claims — exactly what is proven vs. pending

**Proven now (sample mode):**
- Zetaris **data model and evidence retrieval** drive every verdict; the sample
  adapter answers the same queries the live adapter will, over synthetic fixtures.
- The evaluator grounds each conclusion in specific cited records and refuses
  unsupported claims (anti-fabrication test).

**Pending / not claimed (Phase 6, blocked on a secret):**
- Live Zetaris REST/Lightning-SQL execution (needs live `ZETARIS_*` and a
  validated request/response contract against a reachable instance).
- Meterless **Nightshift** live model calls and a **Nightshift receipt** naming the
  real provider/model (needs `METERLESS_RUNTIME_TOKEN`).
- **Nemotron** contributing to a working feature via Nightshift.
- **Scout Intent** distinguishing the hero query from a non-matching query. Until
  verified, routing is deterministic and labelled `fallback` — **never** Scout
  Intent. Sample mode is **not** presented as sponsor proof.

---

## 6. Final PASS/FAIL self-assessment checklist

| Criterion | Result | Evidence |
|---|---|---|
| Real, high-stakes problem with measurable impact | ✅ PASS | beachhead: institutional supplier AR; revenue-at-risk quantified per case |
| Working, reliable agent (thin slice end-to-end) | ✅ PASS | `POST /run` sample pipeline; 68 tests; HTTP e2e |
| Explainable, evidence-backed reasoning | ✅ PASS | supported/rejected causes + cited evidence + trace |
| Anti-fabrication (no claim without grounding) | ✅ PASS | remove-CMP-005 ⇒ insufficient (test + `README` §3) |
| Multiple grounded inputs (not one hard-coded answer) | ✅ PASS | `INV-004/005/006` → H4/H1/H5 |
| Strong, reproducible demo | ✅ PASS | `input_examples/`, `output_examples/`, `logs/`, CI green on clean clone |
| Product & UX (professional workspace) | ✅ PASS | React/Vite workspace + trace panel; `tsc -b && vite build` |
| Zetaris is the evidence layer | ✅ PASS (sample) | all evidence via `ZetarisAdapter`; live path gated |
| Nightshift for all product AI | ⛔ NOT CLAIMED | live path blocked on `METERLESS_RUNTIME_TOKEN` (Phase 6) |
| Nemotron via Nightshift | ⛔ NOT CLAIMED | pending Phase 6 receipt |
| Scout Intent live routing | ⛔ NOT CLAIMED | fallback router, honestly labelled |
| No secrets committed / `.env` never read | ✅ PASS | `.gitignore`, `AGENTS.md`, config reads `os.environ` only |
| No chain-of-thought / secrets in traces | ✅ PASS | operational trace only; masked repr; NAMES-only errors |
| Human approval on actions | ✅ PASS | approval gate (explain-only acknowledgement) |
| CI + clean-clone reproducibility | ✅ PASS | GitHub Actions backend+frontend green on empty env |
| Submission **not** created prematurely | ✅ PASS | this file prepares only; see §7 |

Legend: ✅ satisfied · ⛔ intentionally not claimed (blocked/deferred), never faked.

---

## 7. Exact remaining **manual** steps (require a human / secret)

These are **not** automated here by design — the autonomous build stops at
secrets and at HackOS actions:

1. **Supply live credentials** in `.env` (owner only — the agent never opens it):
   `METERLESS_BASE_URL`, `METERLESS_RUNTIME_TOKEN`, `METERLESS_MODEL`,
   `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`. Then complete
   **Phase 6** (real Nightshift request + receipt, Nemotron feature, Scout Intent
   routing proof) and tag `phase-06-meterless-nemotron`.
2. **Create the HackOS submission** on the platform: title, tagline, description
   (draft in `metadata.json`), track = Track 2, team roster (three members,
   unchanged), repository link, and any required sponsor-tech attestations.
3. **Record & upload the demo video** (script §2) and **publish the deck**
   (outline §3, shots §4).
4. **Verify live-mode screenshots** once Phase 6 receipts exist, then update §5
   claims from ⛔ to ✅ only where actually proven.

---

## 8. `metadata.json`

A submission-metadata **draft** is provided at [`metadata.json`](metadata.json)
for the human steps in §7. It contains no secrets and makes no unproven claim;
the values marked `TBD` are for the owner to confirm on the HackOS form.
