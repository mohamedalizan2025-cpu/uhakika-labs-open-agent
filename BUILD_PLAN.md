# BUILD_PLAN.md — Uhakika Implementation Plan (9-Phase Checkpoint Protocol)

> **Status:** Governing build plan. No investigation features are implemented yet.
> This plan is aligned to the approved technical stack and the canonical
> environment-variable contract. Each phase ends with tests → diff review →
> secret scan → BUILD_LOG update → commit → push `main` → phase tag.

---

## 0. Completed groundwork

- Git repo on branch `main`; baseline commit `chore: capture pre-build scaffold and git setup`; specification commit `docs: establish Uhakika product and agent specifications`.
- `.env`, `.venv/`, caches ignored (`.gitignore` will gain frontend/cache entries during Phase 2).
- Zetaris running locally, verified 9/9.
- Phase 2 documentation/skeleton pass produced `agent/config.py`, adapter interfaces, and stdlib tests (reconciled in Phase 2 below).

---

## 1. Team & Roles (provisional)

| Person | Provisional role | Primary focus |
|---|---|---|
| **Ali** | Product owner | AI/data, integration, sponsor technology, architecture |
| **Friend 1** | Frontend / UI / UX | Investigation Workspace, evidence cards, approval gate, trace view |
| **Friend 2** | Backend / integrations / testing | Agent orchestration, Zetaris client, Nightshift client, tests |

The HackOS team remains three members; one member implements. Do not alter the roster or create a HackOS submission.

---

## 2. Approved technical stack

**Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic, httpx, python-dotenv, pytest.
**Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Lucide React, TanStack Query; Recharts only when a chart materially helps.
**Architecture:** `frontend/` holds the React app; FastAPI owns the backend/API; Vite proxies the backend in dev; a production frontend build may be served by FastAPI. No Next.js. No plain static HTML as the main interface. No Supabase/Postgres/Mongo/extra DB for V0. Zetaris is the mandatory live data layer; reproducible synthetic CSV fixtures back the V0 datasets; sample mode uses a credential-free adapter over the same fixtures.

If Python 3.14 proves incompatible with a dependency, **stop** — do not swap Python automatically. If Node is incompatible with Vite, **stop** — do not install/replace Node automatically.

---

## 3. Canonical environment variables (only these names)

`METERLESS_BASE_URL`, `METERLESS_RUNTIME_TOKEN`, `METERLESS_MODEL`, `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`, `SAMPLE_MODE`, `MAX_EVIDENCE_RETRIES`.

Prohibited legacy aliases (never supported/documented/migrated): `METERLESS_API_KEY`, `NEMOTRON_MODEL`, `ZETARIS_BASE_URL`. `.env` is never opened/read/printed; missing variables are reported by **name only**.

Model routing: the live route is read from `METERLESS_MODEL` and served through Nightshift; Nemotron powers EvaluatorAgent; OpenRouter sits *behind* Nightshift only. Preferred test route (config only): `nvidia/nemotron-3.5-super-vl:free`. Never claim a provider/model without a Nightshift receipt.

---

## 4. Prioritization (judging weights)

Impact 30 · Technical 20 · Innovation 15 · Demo 15 · Product & UX 10 · Sponsor Tech 10.
Optimize in order: **real problem/impact → working reliable agent → evidence-backed reasoning → strong demo → UX → extras.** Build the end-to-end thin slice early. A reliable thin slice beats a broken wide build.

---

## 5. Phase checkpoint protocol (run at the end of every phase)

1. Run all relevant backend and frontend tests.
2. Run frontend type-check + production build when frontend files changed.
3. Inspect the complete diff.
4. Verify the phase acceptance criteria.
5. Secret-scan tracked files **without printing matched secret content**.
6. Update `BUILD_LOG.md` honestly.
7. Stage only phase-related files.
8. Run `git diff --cached --check`.
9. Commit with one focused message.
10. Push `main`.
11. Create + push the phase tag if it does not exist (never move/force an existing tag).
12. Continue automatically when green. **Never commit a failing phase.**

**GitHub:** reuse `origin` if configured; else create/reuse the public repo `uhakika-labs-open-agent` (gh is authenticated). Preserve local history; never create a duplicate; never force-push or rewrite history.

---

## 6. Phases

### Phase 1 — Specification (Document Correction Gate)
- Update the six governing docs to the canonical env names + approved React/Vite stack; Scout Intent = required live-routing Engine (`fallback` labeled); Nemotron-via-Nightshift powers EvaluatorAgent; sample mode credential-free but insufficient as sponsor proof; keep three core agents, one `POST /run`, one Investigation Workspace + Trace Panel; World Model / ActionAgent deferred.
- Acceptance: docs internally consistent; no legacy aliases in normative docs; no feature falsely claimed complete; no secrets.
- **Commit:** `docs: align specifications to canonical contracts and approved stack`
- **Tag:** `phase-01-specification`

### Phase 2 — Foundation
- Reconcile existing Phase 2 work. Python package structure; central validated config (canonical names, legacy ignored, secrets masked); FastAPI app factory + `/health`; Zetaris + Nightshift adapter boundaries; domain models; sanitized operational logging; `.env.example` (canonical names, placeholders only); pytest tests; React/TypeScript/Vite scaffold with Tailwind + approved UI deps; basic app shell; TanStack Query provider; API client boundary; error boundary; loading/empty states; backend + frontend dev instructions.
- Tests prove: legacy aliases ignored; canonical names load; secrets never appear in repr/status/errors; sample mode starts without credentials; live mode reports missing names only; `/health` works; `POST /run` is **not** implemented during foundation; frontend type-check + production build pass.
- **Commit:** `fix: align contracts and complete application foundation`
- **Tag:** `phase-02-foundation`

### Phase 3 — Zetaris Data
- Inspect safe files (`hello.py`, `smoke_test.py`) — never `.env`. Synthetic CSV fixtures for all hero datasets + `dataset_meta`; stable evidence IDs; normalized evidence envelopes; completeness validation; credential-free sample evidence adapter; live Zetaris REST adapter; one statement per request; fresh request ID per query; sanitized errors; empty-result handling; typed domain conversion; tests for malformed/incomplete evidence. Validate the Lightning-SQL contract from verified code/live service — do not invent fields.
- Run `SELECT 1 AS one` only if credentials already configured (never expose auth). Then seed/expose hero datasets through Zetaris and prove they are queryable.
- **Commit:** `feat: establish Zetaris evidence layer`
- **Tag:** `phase-03-zetaris-data`

### Phase 4 — Agent Thin Slice
- Real sample-mode pipeline: `POST /run` → routing interface → InvestigatorAgent → EvidenceAgent → evidence adapter → EvaluatorAgent → supported/rejected hypotheses → recommendation → human-approval state → operational trace. Conclusions derived at runtime; no stored hero answer; INV-004 → TZS 126,000,000; H4 depends on CMP-005 + CLAUSE-7.2; MSG-037 is corroboration only; H1–H3 rejected with evidence reasons; removing CMP-005 downgrades H4; every claim cites evidence IDs; missing evidence → insufficient evidence; traces are actions/decisions (never chain-of-thought); bounded retries; Pydantic request/response contracts; contract + mutation + anti-fabrication tests.
- **Commit:** `feat: implement evidence-grounded agent thin slice`
- **Tag:** `phase-04-agent-thin-slice`

### Phase 5 — Evaluator Loop
- Bounded retrieval retries; evaluator critique; insufficient-evidence behavior; malformed-model-output handling; approval state; deterministic sample routing labeled `fallback`; multiple inputs (not only the hero query); confidence validation; evidence-removal / retry-limit / failure-state tests. Never label the fallback as Scout Intent.
- **Commit:** `feat: harden evaluator and retry loop`
- **Tag:** `phase-05-evaluator-loop`

### Phase 6 — Meterless, Nightshift, Nemotron (live path)
- Scout Intent powers live routing; every live model request passes through Nightshift; Nemotron powers EvaluatorAgent critique; model output validated before affecting conclusions; evidence rules override unsupported model claims; routing stays configuration-driven; sanitized receipt metadata captured.
- Required proof: (1) Scout Intent distinguishes the hero query from a non-matching query; (2) a real request passes through Nightshift; (3) a Nightshift receipt identifies the actual provider/model; (4) Nemotron contributes to a working feature; (5) no credentials in logs/traces.
- **If the runtime token / model / provider needs a human, STOP with `ENTER SECRET HERE` and name the exact variable.** Do not claim this phase from mocks or sample mode.
- **Commit:** `feat: integrate Scout Intent and Nemotron through Nightshift`
- **Tag:** `phase-06-meterless-nemotron`

### Phase 7 — Professional Investigation Workspace (React)
- Enterprise-grade single Investigation Workspace + Trace Panel. Visual direction: serious institutional-finance product; deep navy/slate nav; warm neutral workspace; emerald=supported/safe; amber=warning/pending; red sparingly for material risk; strong type/spacing; subtle borders/shadows; no gradient/glass overuse; no fake metrics; no lorem ipsum; restrained transitions; WCAG-conscious contrast + keyboard. Includes top bar/identity, question composer, invoice/contract context, prominent TZS revenue-at-risk, agent execution progress, hypothesis cards + statuses, supported/rejected causes, evidence cards (IDs + source summaries), recommendation panel, human-approval control, live/sample badge, expandable Trace Panel, loading skeletons, empty/insufficient-evidence/runtime-unavailable/retry/success states. shadcn/ui used thoughtfully; Lucide icons (no emoji); Recharts only for genuinely useful risk/timeline. Connect to the real FastAPI contract via TanStack Query; **do not hardcode the hero result in components.**
- Test: TypeScript, production build, API state handling, sample workflow, error states, responsive layout, keyboard-accessible critical controls.
- **Commit:** `feat: deliver professional investigation workspace`
- **Tag:** `phase-07-investigation-ui`

### Phase 8 — Hardening
- Full backend tests; frontend tests/type-check/build; clean-clone validation where safe; GitHub Actions for credential-free backend tests + frontend build; verify sample mode needs no credentials; verify no hardcoded conclusions; verify no live evidence bypasses Zetaris; verify all live AI goes through Nightshift; verify no secrets/chain-of-thought in traces; ≥3 sample inputs/outputs; complete setup/usage/architecture docs; test Windows clean-start.
- **Commit:** `test: harden reproducibility and sponsor boundaries`
- **Tag:** `phase-08-hardening`

### Phase 9 — Submission Preparation (prepare, do not submit)
- Final public README; architecture diagram; sponsor-tech explanation; demo script; slide-deck outline; `metadata.json`; three sample inputs/outputs; sanitized trace; screenshots plan; clean-clone instructions; pre-existing-component declaration; final PASS/FAIL checklist; exact remaining manual submission steps.
- Do **not**: create the HackOS submission, alter the roster, upload the demo video, publish the deck, expose credentials, or claim an unproven integration.
- **Commit:** `docs: prepare reproducible hackathon submission`
- **Tag:** `phase-09-submission-ready`

---

## 7. Submission artifacts (produced across phases)

`README.md`, `.env.example` (canonical names, placeholders only — never real secrets), `input_examples/`, `output_examples/`, `logs/` (sample operational trace), and a clean-clone validation. Installs happen only inside `.venv` and `frontend/`; `requirements.txt` + `package-lock.json` record approved direct dependencies.

---

## 8. Stretch / Deferred (do NOT build unless the thin slice is solid)

`ActionAgent` as a separate agent, World Model, guarantees-based workflow, portfolio dashboards, multiple UI pages, real-time streaming, complex authentication, multiple REST endpoints (only `POST /run` is required), production-grade infrastructure.

---

## 9. Cross-cutting rules

- Zetaris for all business evidence; Nightshift for all product AI; model route via `METERLESS_MODEL`; never invent IDs/endpoints/credentials.
- Never open/read/print `.env`. Secrets referenced by name only; missing-variable errors show names only.
- Sample mode is credential-free but never presented as sponsor proof.
- Small, reversible commits; human approval before commit only where the governing workflow still requires it; explain-before-change for non-routine edits.
- Update `BUILD_LOG.md` every phase; keep `TBD`s honest.
- **Stop conditions:** a secret/login must be entered; GitHub auth needs a human; Node/Python must be installed/replaced; a destructive op appears necessary; documents contain an unresolved contradiction; tests fail with no clear safe fix; the live Zetaris contract cannot be verified; Nightshift needs human UI interaction; a major out-of-scope product decision is required; a HackOS roster/submission action is reached; Phase 9 is complete; or continuing risks credentials or existing work.
