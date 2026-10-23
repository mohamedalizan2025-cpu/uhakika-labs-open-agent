"""Zetaris adapter selection (single boundary for the EvidenceAgent).

Returns the credential-free ``SampleZetarisAdapter`` when ``SAMPLE_MODE`` is on and
the ``LiveZetarisAdapter`` otherwise. The rest of the app depends only on the
``ZetarisAdapter`` interface, so live and sample modes exercise the SAME pipeline.

No credentials are hardcoded or read here — configuration is injected via
``Settings`` (which never touches ``.env``).
"""
from __future__ import annotations

from agent.config import Settings
from agent.tools_zetaris import ZetarisAdapter
from agent.zetaris_live import LiveZetarisAdapter
from agent.zetaris_sample import SampleZetarisAdapter


def build_zetaris_adapter(settings: Settings) -> ZetarisAdapter:
    """Build the appropriate Zetaris adapter for the configured mode."""
    if settings.sample_mode:
        return SampleZetarisAdapter()
    return LiveZetarisAdapter(settings)
