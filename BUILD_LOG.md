# BUILD_LOG.md — Uhakika Engineering Journal

> **Rule:** This is a chronological, factual engineering log. **Record only what actually happened.** Do **not** invent work, results, tests, or claims. If something has not occurred, it does not appear as if it did. Newest entries at the top.

---

## Entry Template (copy for future entries)

```
Date/time:
Person:
Goal:
Change:
Files touched:
Models/tools used:
Tests:
Result:
Problems:
Decision:
Next:
```

---

## Log Entries

```
Date/time: Pre-build window (before official start)
Person: Ali (with team)
Goal: Establish startup direction and validate sponsor prerequisites.
Change: Project research completed; startup direction locked as
        "Institutional Contract Revenue Assurance" (beachhead: Tanzania
        public-sector/institutional suppliers). Zetaris installed locally
        and verified (9/9 checks passed). Repository scaffold created
        ahead of product implementation (empty agent/*.py, smoke_test.py,
        prompts/, hello.py placeholder).
Files touched: hello.py, smoke_test.py, agent/llm.py, agent/main.py,
        agent/tools_zetaris.py, prompts/ (created, empty), .env (keys added,
        values empty), .gitignore.
Models/tools used: none for product logic (no product code yet).
Result: Zetaris verified 9/9 locally. No Uhakika product functionality
        implemented. Nightshift setup begun but incomplete.
Problems: Meterless Nightshift runtime URL/token not yet available; direct
        NVIDIA/Nemotron verification problematic for Tanzania.
Decision: Keep model/runtime routing configurable; never invent endpoints,
        model IDs, or credentials.
Next: Initialize Git during build window; then documentation/specification.
```

```
Date/time: Official build window — Session 1
Person: Ali (assistant-driven via Qoder/Qwen build tooling)
Goal: STEP 1 — bring the project under version control safely.
Change: Initialized Git repository (git init) in the existing folder.
        Verified .gitignore rules take effect.
Files touched: .git/ created (no application files altered).
Models/tools used: Qoder IDE + Qwen (build tooling only — NOT product runtime).
Tests: git check-ignore confirmed .env and .venv/ are ignored (by .gitignore
        lines 1 and 2). git status showed both absent from tracked/untracked.
Result: Repository initialized on branch "master". .env and .venv/ confirmed
        ignored. No files added or committed yet.
Problems: None.
Decision: Never force-add .env.
Next: Rename branch to main; make baseline scaffold commit.
```

```
Date/time: Official build window — Session 2
Person: Ali (assistant-driven)
Goal: STEP 2 — record the empty pre-build scaffold as a baseline.
Change: Renamed branch master -> main. Staged only .gitignore, hello.py,
        smoke_test.py, agent/llm.py, agent/main.py, agent/tools_zetaris.py.
        Verified .env and .venv/ were NOT staged. Committed baseline.
Files touched: committed 6 files (5 inserted lines total: 4 in .gitignore,
        1 in hello.py; the other 4 files were empty).
Models/tools used: Qoder IDE + Qwen (build tooling only).
Tests: git diff --cached --name-only before commit listed exactly the 6
        approved files (no .env, no .venv/). Post-commit git log --oneline -1
        = e014cd2 "chore: capture pre-build scaffold and git setup".
Result: Baseline commit e014cd2 on branch main; working tree clean. .env
        remains ignored with empty values (no secrets committed).
Problems: Shell stripped quotes on the first commit attempt (message split
        into pathspecs); that attempt failed harmlessly with no commit.
        Resolved by committing via a temp message file inside .git/ then
        deleting it. No application code affected.
Decision: Baseline captures the empty scaffold so later work diffs cleanly.
Next: Phase 1 documentation/specification.
```

```
Date/time: Official build window — Session 3 (Phase 1)
Person: Ali (assistant-driven)
Goal: Phase 1 — create the six specification documents. No product code.
Change: Authored AGENTS.md, PRD.md, ARCHITECTURE.md, DATA_CONTRACT.md,
        BUILD_PLAN.md, and this BUILD_LOG.md at project root.
Files touched: AGENTS.md, PRD.md, ARCHITECTURE.md, DATA_CONTRACT.md,
        BUILD_PLAN.md, BUILD_LOG.md (all new, documentation only).
Models/tools used: Qoder IDE + Qwen (build tooling only).
Tests: none (documentation phase). Intended validation is human review
        against AGENTS.md rules.
Result: Six spec files created. No Python/frontend code written, no packages
        installed, .env untouched, existing Python files unaltered, no APIs
        implemented. Undecided items explicitly marked TBD.
Problems: None. Noted and avoided: no invented endpoints/model IDs/credentials.
        (Zetaris base URL and SQL endpoint used only because provided in the
        task; Nightshift URL/token and Nemotron model ID left TBD.)
Decision: Keep sample-mode fallback and configurable routing as core risk
        mitigations while Nightshift runtime setup completes.
Next: Stop for human review of the six documents (no commit yet).
```

```
Date/time: Official build window — Session 4 (Phase 1 audit + documentation correction)
Person: Ali (assistant-driven)
Goal: Run a strict cross-document consistency audit of the six spec files, then
        apply the approved documentation corrections. Documentation only.
Change: Applied audit findings across AGENTS.md, PRD.md, ARCHITECTURE.md,
        DATA_CONTRACT.md, BUILD_PLAN.md. Locked V0 to three core agents
        (Investigator/Evidence/Evaluator; ActionAgent = STRETCH), a routing
        stage (Scout Intent = a Meterless Engine candidate, TBD), and a single
        judge-facing POST /run (PLANNED, not implemented). Added a
        compliance_items dataset to ground H4, clause_ref for clause
        traceability, invoices.required_submission_date for the H3 lateness
        rule, an explicit hypothesis->data mapping, and a shared case-state
        object. Collapsed UI to one Investigation View + Trace Panel. Corrected
        sample-mode wording: SAMPLE_MODE executes the real pipeline and derives
        conclusions at runtime (never a stored answer). Added AGENTS.md rules
        (no-hardcoded-conclusions, scope/sponsor/doc-sync/conflict-stop,
        Cursor-optional/Qoder-allowed, credential hygiene) and BUILD_PLAN
        submission artifacts + stretch list. Streaming marked stretch only.
Files touched: AGENTS.md, PRD.md, ARCHITECTURE.md, DATA_CONTRACT.md,
        BUILD_PLAN.md, BUILD_LOG.md (documentation only).
Models/tools used: Qoder IDE + Qwen (build tooling only — NOT product runtime).
Tests: none (documentation phase). A re-read/re-audit of all six files was
        performed for consistency; findings reported to the human.
Result: No product functionality implemented. No packages installed. .env
        untouched. Existing Python files unaltered. Nightshift setup still
        incomplete. Scout Intent still planned/TBD. Nemotron route still TBD.
        POST /run still planned (no code). No new features claimed as built.
Problems: None. The correction pass makes no implementation claims.
Decision: Documentation-only; keep all TBD items honest; do not commit yet.
Next: Await human review of the corrected spec set.
```

```
Date/time: Official build window — Session 5 (Phase 2 skeleton)
Person: Ali (assistant-driven via Qwen build tooling only)
Goal: Phase 2 — minimal Python/FastAPI project skeleton, central config, clean
        Zetaris + Nightshift adapter interfaces, credential-free tests. NO
        investigation features.
Change: Added agent/__init__.py and agent/config.py (reads ONLY the canonical
        env names METERLESS_BASE_URL / METERLESS_API_KEY / NEMOTRON_MODEL from
        os.environ; never touches .env; secret masked via dataclass repr=False;
        no hardcoded endpoints/model IDs). Filled the three empty stubs with
        interface/skeleton code: tools_zetaris.py = ZetarisAdapter ABC +
        ZetarisQueryResult; llm.py = NightshiftAdapter ABC + CompletionRequest/
        Result; main.py = FastAPI create_app + /health liveness only (NO POST
        /run). Added tests/ (stdlib unittest: test_config, test_adapters,
        test_app) and requirements.txt (deps DECLARED but NOT installed).
Files touched: agent/__init__.py, agent/config.py, agent/tools_zetaris.py,
        agent/llm.py, agent/main.py, tests/__init__.py, tests/test_config.py,
        tests/test_adapters.py, tests/test_app.py, requirements.txt, BUILD_LOG.md.
Models/tools used: Qoder IDE + Qwen 3.8 Flash (build tooling only — NOT product
        runtime). No OpenRouter extension installed.
Tests: `.venv\Scripts\python.exe -m unittest -v tests.test_config
        tests.test_adapters tests.test_app` -> Ran 12 tests, OK (11 passed,
        1 skipped because fastapi is not installed). No network, no credentials,
        no .env access used.
Result: Credential-free config + adapter-boundary tests pass. No investigation
        features implemented. Nothing committed. .env never opened/read/printed.
Problems: fastapi/uvicorn/pytest are absent in .venv (Python 3.14.7 present), so
        the app module import test is skipped and the server is not runnable yet.
        No canonical env-var NAME exists yet for the Zetaris base URL.
Decision: Used stdlib unittest (not pytest) and a dependency-light
        dataclass/ABC config so the safe tests run with zero installs; kept
        agent/__init__.py free of FastAPI imports so config/adapter tests import
        cleanly. Deferred all installs to an owner-approved step.
Next: Await approval + Phase 3 (approve install, bless a canonical Zetaris base-
        URL env name, then wire real live+sample Zetaris adapters, seed hero
        datasets, enforce one-statement/fresh-request-ID, add POST /run).
```

```
Date/time: Official build window — Session 6 (Phase 1 canonical-contract document-correction gate)
Person: Ali (assistant-driven via Qwen 3.8 Flash build tooling only)
Goal: Apply the approved technical-stack and canonical-environment-variable
        corrections across the six governing documents before product build. No
        product features implemented.
Change: AGENTS.md, PRD.md, ARCHITECTURE.md, DATA_CONTRACT.md aligned to the eight
        canonical env names (METERLESS_BASE_URL, METERLESS_RUNTIME_TOKEN,
        METERLESS_MODEL, ZETARIS_REST_URL, ZETARIS_ORG_ID, ZETARIS_API_KEY,
        SAMPLE_MODE, MAX_EVIDENCE_RETRIES); legacy aliases (METERLESS_API_KEY,
        NEMOTRON_MODEL, ZETARIS_BASE_URL) marked ignore-only. Scout Intent set as
        the REQUIRED live-routing Meterless Engine (deterministic `fallback`
        labeled until verified). Nemotron-via-Nightshift = EvaluatorAgent's live
        critique model; OpenRouter kept behind Nightshift (no direct calls, no
        extension). Frontend changed from TBD/static to React+TypeScript+Vite+
        Tailwind+shadcn/ui+Lucide+TanStack Query (Vite proxies FastAPI; prod build
        served by FastAPI; no Next.js/extra DB). Single UI renamed to Investigation
        Workspace + Trace Panel. Sample mode = credential-free but insufficient as
        sponsor proof. BUILD_PLAN rebuilt as the 9-phase checkpoint protocol with
        commit messages + tags. Installs permitted only inside .venv/frontend.
Files touched: AGENTS.md, PRD.md, ARCHITECTURE.md, DATA_CONTRACT.md,
        BUILD_PLAN.md, BUILD_LOG.md (documentation only).
Models/tools used: Qoder IDE + Qwen 3.8 Flash (build tooling only — NOT product runtime).
Tests: none (documentation phase). Re-read of all six docs for consistency; repo
        grep for legacy aliases and a tracked-file secret scan (names/lines only).
Result: No product functionality implemented. .env never opened/read/printed. No
        packages installed. No endpoints/model IDs/tokens/conclusions hardcoded.
        Nightshift / Scout Intent / Nemotron / POST /run still TBD (no code).
Problems: .env currently exposes only the legacy aliases; the owner must populate
        the canonical variables for live modes (the agent never edits .env).
Decision: Treat the six corrected documents as binding and internally authoritative.
Next: Phase 2 foundation — install approved deps in .venv; reconcile config to
        canonical names + tests; add .env.example; FastAPI /health; adapter
        boundaries; React/Vite scaffold. Continue autonomously; stop only on
        genuine blockers.
```

---

## Known Open Items (as of the Phase 1 canonical-contract document-correction gate)

- Meterless Nightshift runtime is still downloading/installing — Runtime URL and token `TBD` (env-provided later).
- Live model route via `METERLESS_MODEL` (Nemotron reached through Nightshift) `TBD` — never claimed without a Nightshift receipt; preferred test route `nvidia/nemotron-3.5-super-vl:free` is configuration only.
- **Scout Intent** is the REQUIRED live-routing Engine — **not yet implemented**; a deterministic `fallback` router is used and labeled until verified.
- Backend (Python/FastAPI) + frontend (React/TypeScript/Vite) stacks are **chosen but not installed**. Internal API routes `TBD`.
- Judge-facing `POST /run` endpoint `TBD` — documented conceptually, **planned, no code exists**.
- **Phase 2 skeleton exists but runs no features:** config module + Zetaris/Nightshift adapter *interfaces* + stdlib-unittest tests are in place; the investigation logic and `POST /run` are still not implemented.
- **`fastapi` / `uvicorn` / `pytest` are NOT installed** (deferred; AGENTS §8). `agent/main.py` imports FastAPI and is exercised only by a skipped test until an owner-approved install.
- Canonical Zetaris variables are defined (`ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`); the owner must populate them in `.env` for live mode (the agent never opens/edits `.env`).
- **`.env` currently exposes only the legacy aliases; the canonical variables are not yet present, so live Zetaris/Nightshift modes cannot run until the owner supplies them.** Sample mode works credential-free.
- No Uhakika product functionality implemented yet.
