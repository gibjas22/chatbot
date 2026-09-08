"""Helpers for turning OpenAI errors into text that is safe to display.

OpenAI puts the offending key straight into the message of an authentication
error, so rendering that verbatim would print a live credential into the page.
Everything shown to a user goes through `safe_error_text` first.
"""

from __future__ import annotations

import re

# Matches the key formats OpenAI issues: the classic `sk-` keys and the
# project-scoped `sk-proj-` ones, both of which share the same prefix.
KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")

MASK = "sk-***"


def safe_error_text(error: object) -> str:
    """Return the error's message with any API key masked.

    Anything else in the message is left alone, because the useful part of a
    rate-limit or connection error is exactly the detail a user needs to act on.
    """
    return KEY_PATTERN.sub(MASK, str(error))
