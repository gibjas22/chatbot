"""Pure helpers for the chatbot's safety and cost controls.

Deliberately free of Streamlit and OpenAI imports so the rules can be tested
without a UI, a network call or a paid API key. `streamlit_app.py` is the only
place those libraries are used.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Limits. Each one bounds a resource that is otherwise unbounded.
MAX_INPUT_CHARS = 4000
MAX_HISTORY_MESSAGES = 20
MAX_OUTPUT_TOKENS = 800
MAX_REQUESTS_PER_SESSION = 50
REQUEST_TIMEOUT_SECONDS = 60.0
MAX_RETRIES = 2

# Rough characters per token for English prose. Used only to warn before a
# request, never to bill or to promise a cost.
APPROX_CHARS_PER_TOKEN = 4

# Credential shapes worth masking if one ever reaches a rendered string.
_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
)

# Link schemes that are safe to click. Anything else is stripped to plain text.
_SAFE_URL_SCHEMES = ("http://", "https://", "mailto:")

_MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(\s*([^)\s]+)[^)]*\)")


@dataclass(frozen=True)
class Validation:
    """The result of checking one piece of user input."""

    ok: bool
    message: str = ""


def redact_secrets(text: str) -> str:
    """Mask anything credential-shaped, keeping the last four characters.

    Applied to every string shown to a user or written to a log, so that a key
    echoed back by a provider error never reaches the page intact.
    """
    if not text:
        return text
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(lambda m: f"{m.group(0)[:3]}...{m.group(0)[-4:]}", result)
    return result


def resolve_api_key(
    operator_secret: str | None,
    environment_value: str | None,
    user_supplied: str | None,
) -> tuple[str | None, str]:
    """Choose which key to use and report where it came from.

    An operator key configured for the deployment wins, so a hosted instance
    does not ask every visitor for one. Otherwise the visitor supplies their
    own, which belongs to their session alone.

    Returns the key and one of "operator", "user" or "none".
    """
    for candidate, source in (
        (operator_secret, "operator"),
        (environment_value, "operator"),
        (user_supplied, "user"),
    ):
        if candidate and candidate.strip():
            return candidate.strip(), source
    return None, "none"


def validate_user_input(text: str, max_chars: int = MAX_INPUT_CHARS) -> Validation:
    """Reject empty or oversized input before it costs anything."""
    if text is None or not text.strip():
        return Validation(False, "Please type a message before sending.")
    if len(text) > max_chars:
        return Validation(
            False,
            f"That message is {len(text):,} characters. "
            f"The limit is {max_chars:,}. Please shorten it and try again.",
        )
    return Validation(True)


def trim_history(
    messages: list[dict[str, str]],
    max_messages: int = MAX_HISTORY_MESSAGES,
) -> list[dict[str, str]]:
    """Keep the most recent turns, and always keep a leading system message.

    Without this the whole conversation is resent on every turn, so cost grows
    with the square of the conversation length and eventually the request
    exceeds the model's context window and fails outright.
    """
    if max_messages <= 0:
        return []

    system = [m for m in messages[:1] if m.get("role") == "system"]
    rest = messages[len(system) :]

    budget = max_messages - len(system)
    if budget <= 0:
        return system
    return system + rest[-budget:]


def estimate_tokens(messages: list[dict[str, str]]) -> int:
    """A rough token estimate, for warning only.

    This is a character-count approximation, not the provider's tokeniser. Never
    present it as an exact figure or as a cost.
    """
    characters = sum(len(m.get("content", "")) for m in messages)
    return characters // APPROX_CHARS_PER_TOKEN


def session_limit_reached(
    request_count: int, limit: int = MAX_REQUESTS_PER_SESSION
) -> bool:
    """Whether this session has spent its allowance of provider calls."""
    return request_count >= limit


def sanitise_markdown_links(text: str) -> str:
    """Defang links whose scheme is not plainly safe.

    Renderers differ in what they permit, so a `javascript:` or `data:` link is
    reduced to its visible text rather than relied upon to be neutralised
    downstream. Safe links are left exactly as written.
    """
    if not text:
        return text

    def replace(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        if url.lower().startswith(_SAFE_URL_SCHEMES):
            return match.group(0)
        if url.startswith(("/", "#", ".")):
            return match.group(0)
        return label or url

    return _MARKDOWN_LINK.sub(replace, text)


def safe_error_message(exc: BaseException) -> str:
    """Turn a provider exception into one line safe to show a user.

    The raw text is redacted rather than trusted, because a provider error can
    quote the request it rejected, and an unhandled exception in Streamlit
    renders a traceback into the browser.
    """
    name = type(exc).__name__
    detail = redact_secrets(str(exc)).strip()

    lowered = detail.lower()
    if "api key" in lowered or "authentication" in lowered or "401" in lowered:
        return "That API key was rejected. Check the key and try again."
    if "rate limit" in lowered or "429" in lowered:
        return "The provider is rate limiting this key. Wait a moment, then retry."
    if "timeout" in lowered or "timed out" in lowered:
        return "The request timed out before the model replied. Please try again."
    if "context length" in lowered or "maximum context" in lowered:
        return "This conversation is too long for the model. Start a new chat."

    if not detail:
        return f"The request failed ({name}). Please try again."
    return f"The request failed ({name}): {detail[:200]}"
