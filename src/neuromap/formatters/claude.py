from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path


def format_claude(neuromap, max_tokens: int = 2000) -> str:
    """
    Generate a CLAUDE.md formatted project map.

    Claude Code automatically reads ``CLAUDE.md`` from the project root as
    background context. This formatter delegates to ``NeuroMap.generate_claude``
    so the generation logic lives in a single place alongside the other
    markdown generators.
    """
    return neuromap.generate_claude(max_tokens)
