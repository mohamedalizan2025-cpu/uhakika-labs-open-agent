"""Generate reproducible sample input/output artifacts (BUILD_PLAN Phase 8).

Runs the REAL sample-mode pipeline (no credentials, no network, never reads
.env) for several invoice IDs and writes:
  - input_examples/<id>.json   the RunRequest sent to POST /run
  - output_examples/<id>.json  the derived RunResponse (conclusions computed
                               at runtime from the fixtures — not stored answers)
  - logs/sample_trace.jsonl    a sanitized OPERATIONAL trace (actions/decisions
                               only; never chain-of-thought, never secrets)

These are documentation artifacts. Nothing in the application reads them, and
sample mode is NOT sponsor proof. `case_id` and trace timestamps vary per run
by design; the grounded fields (cause, revenue, rejected set, evidence IDs) are
deterministic for the given fixtures.

Usage (from the repo root):
    python scripts/generate_examples.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.config import Settings  # noqa: E402
from agent.investigator_agent import InvestigatorAgent  # noqa: E402
from agent.models import RunRequest  # noqa: E402

CASES: list[tuple[str, str]] = [
    ("INV-004", "Why hasn't our TZS 126,000,000 invoice been paid?"),
    ("INV-005", "Why is the health-depot delivery invoice INV-005 unpaid?"),
    ("INV-006", "Everything is delivered and accepted for INV-006 — why is payment stuck?"),
]


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    settings = Settings(sample_mode=True)
    in_dir = ROOT / "input_examples"
    out_dir = ROOT / "output_examples"
    logs_dir = ROOT / "logs"
    for directory in (in_dir, out_dir, logs_dir):
        directory.mkdir(exist_ok=True)

    for invoice_id, question in CASES:
        request = RunRequest(question=question, invoice_id=invoice_id, sample_mode=True)
        response = InvestigatorAgent(settings).run(request)
        _write_json(in_dir / f"{invoice_id}.json", request.model_dump())
        _write_json(out_dir / f"{invoice_id}.json", response.model_dump())

    # One sanitized operational trace as a representative log sample.
    hero = InvestigatorAgent(settings).run(
        RunRequest(question=CASES[0][1], invoice_id=CASES[0][0], sample_mode=True)
    )
    header = (
        f"case_id={hero.case_id} invoice_id={CASES[0][0]} mode=SAMPLE "
        "# operational trace only — no reasoning, no secrets"
    )
    lines = [header] + [json.dumps(entry.model_dump(), ensure_ascii=False) for entry in hero.trace]
    (logs_dir / "sample_trace.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"generated {len(CASES)} sample input/output pairs + 1 trace log")


if __name__ == "__main__":
    main()
