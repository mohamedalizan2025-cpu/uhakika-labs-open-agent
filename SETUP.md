# Setup & Reproducibility Runbook

This is the local setup, usage, and reproducibility guide for **Uhakika Labs —
Institutional Contract Revenue Assurance**. The public-facing README is produced
in Phase 9; this document is the engineering runbook.

Everything here runs **credential-free in sample mode**. The `.env` file is
Git-ignored and loaded only by the runtime configuration mechanism via
`python-dotenv` (values are never logged or exposed). The AI/operator never
opens, reads, displays, or reports `.env` contents.

---

## 1. Prerequisites

| Tool    | Version                | Notes                                        |
|---------|------------------------|----------------------------------------------|
| Python  | 3.11+ (validated 3.14) | Backend + tests                              |
| Node.js | 20+ (validated 26)     | Frontend dev/build                           |
| npm     | 10+                    | Installs are scoped to `frontend/` only      |

No global package installs. Backend deps live in `.venv`; frontend deps live in
`frontend/node_modules` (both are git-ignored).

---

## 2. Backend

```bash
# from the repo root
python -m venv .venv
.venv\Scripts\activate            # Windows   (source .venv/bin/activate on *nix)
pip install -r requirements.txt
```

`requirements.txt` pins the direct dependencies (fastapi, uvicorn, httpx, pytest,
pydantic, python-dotenv) plus one transitive for reproducibility (starlette).

Run the API (sample mode):

```cmd
set SAMPLE_MODE=true
.venv\Scripts\python.exe -m uvicorn agent.main:app --reload --port 8000
```

Alternatively, create a local `.env` in the repo root (Git-ignored) with:
```
SAMPLE_MODE=true
```
The application loads it automatically via `python-dotenv` (OS env vars take
precedence over `.env`).

- `GET  /health` → operational readiness (ok, default_mode, sample_ready, live_ready, integrations, missing_env_names).
- `POST /run` → runs the investigation pipeline; `sample_mode` is required in every request.

> `SAMPLE_MODE` defaults to **false**. If it is unset the app attempts live mode,
> which fails closed with a NAMES-only configuration error until the canonical
> live variables are populated and the live contract is validated (Phase 6).

### Configuration (canonical environment names only)

See `.env.example` (placeholder values only — never commit a real `.env`):

| Variable                  | Purpose                                   | Secret? |
|---------------------------|-------------------------------------------|---------|
| `METERLESS_BASE_URL`      | Nightshift runtime base URL               | no      |
| `METERLESS_RUNTIME_TOKEN` | Nightshift runtime token                  | **yes** |
| `METERLESS_MODEL`         | Nemotron model route (config, not a claim)| no      |
| `ZETARIS_REST_URL`        | Zetaris REST base URL                      | no      |
| `ZETARIS_ORG_ID`          | Zetaris organisation id                    | no      |
| `ZETARIS_API_KEY`         | Zetaris API key                            | **yes** |
| `SAMPLE_MODE`             | `true` → credential-free fixture pipeline  | no      |
| `MAX_EVIDENCE_RETRIES`    | Bounded evidence-retry budget (default 3)  | no      |

Legacy aliases (`METERLESS_API_KEY`, `NEMOTRON_MODEL`, `ZETARIS_BASE_URL`) are
ignored, never read or migrated.

---

## 3. Frontend

```bash
cd frontend
npm ci                            # clean install from package-lock.json
npm run dev                       # http://localhost:5173 (proxies /health, /run to :8000)
npm run test:run                  # run Vitest runtime tests
```

- Start the backend first (section 2), then `npm run dev`, then open the preview.
- The guided-demo button fires INV-004 (sample mode) on click — page load alone does NOT auto-run.
- To enable auto-run on page load for hackathon video capture: set `VITE_DEMO_AUTORUN=true` in `frontend/.env`.
- Production build / type-check: `npm run build` (runs `tsc -b && vite build`).

The dev server proxies `/health` and `/run` to `http://localhost:8000`; no API
host or credential is hardcoded in the UI.

---

## 4. Tests

```bash
# from the repo root
.venv\Scripts\python.exe -m pytest -q     # 68 tests

# frontend
cd frontend && npm run test:run            # 14 Vitest tests
```

The warning policy lives in `pytest.ini` (first-party `UserWarning`s are promoted
to errors; the third-party starlette `TestClient` deprecation is ignored) so the
command is the same locally and in CI.

68 tests cover: canonical config contracts (names-only errors, secret masking),
`.env.example` contract, the credential-free sample Zetaris adapter, fixture
integrity + DATA_CONTRACT validation, the live-adapter config gate + one-statement
rule, the factory, the intent router (always `fallback`), the evaluator rule
engine (grounding, anti-fabrication, evidence-removal downgrade, bounded retries,
adapter-failure → honest insufficient), the model-critique safety boundary
(clamped confidence, status never overridden, malformed input ignored), and HTTP
e2e for three distinct inputs. No test touches the network, a credential, or `.env`.

Regenerate the sample artifacts:

```bash
.venv\Scripts\python.exe scripts\generate_examples.py
```

---

## 5. Clean-clone validation

A fresh clone must build and test with an **empty environment**:

```bash
git clone <repo> && cd <repo>
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                              # green with no env vars set
cd frontend && npm ci && npm run test:run && npm run build   # green
```

GitHub Actions (`.github/workflows/ci.yml`) runs exactly this on every push to
`main` and on pull requests — the backend job asserts no `.env` is committed.

---

## 6. Windows clean-start notes

- The shell here is `cmd.exe`. Set env vars with `set VAR=value` in the same
  session before launching a command.
- Use the venv interpreter explicitly: `.venv\Scripts\python.exe ...`.
- Unix-only tools are not required; there is no `make`/`bash` dependency.

---

## 7. Sponsor-boundary verification checklist (Phase 8)

- **Sample mode needs no credentials** — verified: the whole suite and the UI run
  with an empty environment (fixtures under `data/fixtures/`).
- **No hardcoded conclusions** — conclusions are derived at runtime by the
  evaluator rule engine; tests remove CMP-005 and assert H4 downgrades. No
  component or module stores a hero answer.
- **All business evidence via Zetaris (live-mode invariant)** — in live mode,
  `EvidenceAgent` only queries through `ZetarisAdapter.run_query`. The sample
  adapter uses fixture CSVs and is NOT Zetaris sponsor proof.
- **All product AI via Nightshift** — the live runtime is reached only through
  `NightshiftAdapter` (Phase 6, not yet wired); sample mode makes **no** model
  call and the trace reports `model_route: none`.
- **Scout Intent is not faked** — routing stays deterministic and is labelled
  `fallback`; it is never mislabelled as Scout Intent until the Engine is verified.
- **No secrets or chain-of-thought in traces** — the trace holds operational
  actions/decisions only; secrets are masked (repr=False) and errors list variable
  NAMES only.
- **≥3 sample inputs/outputs** — `input_examples/` and `output_examples/` ship
  INV-004 (H4), INV-005 (H1), INV-006 (H5).

---

## 8. What is blocked

**Phase 6 (live path)** is blocked on a secret the owner must supply: the
`METERLESS_RUNTIME_TOKEN` (plus `METERLESS_BASE_URL`, `METERLESS_MODEL`) and the
live `ZETARIS_*` values, together with validation of the live Lightning-SQL
request/response contract against a reachable service. Until then the live
adapters fail closed (NAMES-only errors) and nothing is claimed from them. Sample
mode is explicitly **not** sponsor proof.
