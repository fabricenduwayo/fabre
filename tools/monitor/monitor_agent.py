"""Cursor SDK agent — the only LLM entry point for the submission monitor.

The monitor never calls OpenAI, Anthropic, or other provider APIs directly.
All auto-fix runs go through cursor_sdk.Agent.prompt with a Composer model slug.
"""

from __future__ import annotations

import os

DEFAULT_CURSOR_MODEL = "composer-2.5"

# Known Cursor Composer slugs; any other composer-* is accepted with a warning.
KNOWN_COMPOSER_MODELS = frozenset(
    {
        "composer-2.5",
        "composer-2.5-fast",
    }
)


def resolve_cursor_model() -> str:
    """Return the Cursor Composer model slug; reject non-Cursor models."""
    raw = (
        os.environ.get("CURSOR_COMPOSER_MODEL", "").strip()
        or os.environ.get("MONITOR_MODEL", "").strip()
        or DEFAULT_CURSOR_MODEL
    )
    model = raw.lower()
    if not model.startswith("composer-"):
        known = ", ".join(sorted(KNOWN_COMPOSER_MODELS))
        raise RuntimeError(
            "Monitor only uses Cursor Composer via cursor_sdk "
            f"(model must start with composer-). Got {raw!r}. "
            f"Examples: {known}. "
            "Set CURSOR_COMPOSER_MODEL=composer-2.5 in tools/monitor/.env"
        )
    return model


def assert_cursor_sdk_only() -> str:
    """Validate config and return the resolved Composer model."""
    return resolve_cursor_model()
