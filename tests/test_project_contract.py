"""Repository contract test — validates `.env.example` against the canonical spec.

This reads the EXAMPLE file only (a normal, tracked file). It NEVER opens, reads,
or prints the real ``.env``. It asserts the shipped example is aligned with the
canonical contract (AGENTS.md §3 / BUILD_PLAN.md §3):

- exactly the eight canonical variable names are present,
- the three prohibited legacy aliases do NOT appear,
- the two secret fields are blank placeholders (no real credential shipped),
- sample mode is on and the retry default is a safe integer.
"""
from __future__ import annotations

from pathlib import Path

from agent.config import (
    CANONICAL_ENV_NAMES,
    ENV_MAX_EVIDENCE_RETRIES,
    ENV_METERLESS_RUNTIME_TOKEN,
    ENV_SAMPLE_MODE,
    ENV_ZETARIS_API_KEY,
    LEGACY_ENV_NAMES,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = REPO_ROOT / ".env.example"


def _parse_example(text: str) -> dict[str, str]:
    """Parse ``KEY=VALUE`` lines, ignoring comments and blanks."""
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def test_example_file_exists_and_is_the_example_not_env() -> None:
    assert EXAMPLE_PATH.is_file()
    # Guard against ever being pointed at the real secret file.
    assert EXAMPLE_PATH.name == ".env.example"


def test_example_declares_exactly_the_canonical_names() -> None:
    keys = set(_parse_example(EXAMPLE_PATH.read_text(encoding="utf-8")).keys())
    assert keys == set(CANONICAL_ENV_NAMES)


def test_example_contains_no_prohibited_legacy_aliases() -> None:
    text = EXAMPLE_PATH.read_text(encoding="utf-8")
    # Legacy names may appear only inside the explanatory prohibition comment,
    # never as an assignable ``KEY=`` line.
    for legacy in LEGACY_ENV_NAMES:
        assert f"{legacy}=" not in text


def test_example_ships_no_real_secret_values() -> None:
    parsed = _parse_example(EXAMPLE_PATH.read_text(encoding="utf-8"))
    # Secret fields must be blank placeholders.
    assert parsed[ENV_METERLESS_RUNTIME_TOKEN] == ""
    assert parsed[ENV_ZETARIS_API_KEY] == ""
    # And no credential-shaped substring anywhere in the example.
    text = EXAMPLE_PATH.read_text(encoding="utf-8")
    for marker in ("sk-", "ghp_", "gho_", "BEGIN PRIVATE KEY"):
        assert marker not in text


def test_example_defaults_to_sample_mode() -> None:
    parsed = _parse_example(EXAMPLE_PATH.read_text(encoding="utf-8"))
    assert parsed[ENV_SAMPLE_MODE].lower() == "true"
    assert parsed[ENV_MAX_EVIDENCE_RETRIES].isdigit()
