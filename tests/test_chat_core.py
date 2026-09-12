"""Regression tests for the chatbot's safety and cost controls.

Every value here is synthetic. No test calls a provider, and no test needs a
real API key.
"""

from __future__ import annotations

import pathlib

import pytest

import chat_core

# Synthetic fixtures, assembled at runtime. Written as literals they would trip
# the repository's own secret scanner, which is working as intended: a scanner
# that has to special-case test files is a scanner with a hole in it.
FAKE_KEY = "sk-" + "A" * 32
FAKE_AWS_KEY = "AKIA" + "IOSFODNN7EXAMPLE"
UNSAFE_HTML_FLAG = "unsafe_allow_html"


# --- credential redaction ------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        FAKE_KEY,
        f"Incorrect API key provided: {FAKE_KEY}. Check your account.",
        f"prefix {FAKE_KEY} suffix",
    ],
)
def test_redact_removes_the_key_body(raw: str) -> None:
    result = chat_core.redact_secrets(raw)
    assert FAKE_KEY not in result
    assert "..." in result


def test_redact_keeps_only_a_short_tail() -> None:
    result = chat_core.redact_secrets(FAKE_KEY)
    # Enough to recognise which key it was, not enough to use it.
    assert result == "sk-...AAAA"


def test_redact_leaves_ordinary_text_alone() -> None:
    text = "The model replied with a summary of the document."
    assert chat_core.redact_secrets(text) == text


def test_redact_handles_other_providers() -> None:
    assert FAKE_AWS_KEY not in chat_core.redact_secrets(FAKE_AWS_KEY)


# --- key resolution and isolation ----------------------------------------


def test_operator_key_wins_over_user_supplied() -> None:
    key, source = chat_core.resolve_api_key("operator-key", None, "user-key")
    assert (key, source) == ("operator-key", "operator")


def test_environment_key_used_when_no_secret() -> None:
    key, source = chat_core.resolve_api_key(None, "env-key", None)
    assert (key, source) == ("env-key", "operator")


def test_user_key_used_when_no_operator_key() -> None:
    key, source = chat_core.resolve_api_key(None, None, "user-key")
    assert (key, source) == ("user-key", "user")


def test_no_key_is_reported_rather_than_guessed() -> None:
    assert chat_core.resolve_api_key(None, None, None) == (None, "none")


def test_whitespace_only_key_is_not_a_key() -> None:
    assert chat_core.resolve_api_key("   ", None, None) == (None, "none")


def test_key_is_stripped() -> None:
    key, _ = chat_core.resolve_api_key(None, None, "  user-key\n")
    assert key == "user-key"


# --- input validation ----------------------------------------------------


def test_empty_input_rejected() -> None:
    assert chat_core.validate_user_input("   ").ok is False


def test_oversized_input_rejected_before_any_call() -> None:
    result = chat_core.validate_user_input("x" * (chat_core.MAX_INPUT_CHARS + 1))
    assert result.ok is False
    assert "limit" in result.message


def test_ordinary_input_accepted() -> None:
    assert chat_core.validate_user_input("Hello there").ok is True


def test_input_exactly_at_the_limit_is_accepted() -> None:
    assert chat_core.validate_user_input("x" * chat_core.MAX_INPUT_CHARS).ok is True


# --- history trimming and cost bounding ----------------------------------


def _turns(count: int) -> list[dict[str, str]]:
    return [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"}
        for i in range(count)
    ]


def test_history_is_bounded() -> None:
    trimmed = chat_core.trim_history(_turns(100))
    assert len(trimmed) == chat_core.MAX_HISTORY_MESSAGES


def test_trimming_keeps_the_most_recent_turns() -> None:
    trimmed = chat_core.trim_history(_turns(100), max_messages=3)
    assert [m["content"] for m in trimmed] == ["m97", "m98", "m99"]


def test_short_history_is_untouched() -> None:
    history = _turns(4)
    assert chat_core.trim_history(history) == history


def test_system_prompt_survives_trimming() -> None:
    history = [{"role": "system", "content": "trusted instructions"}] + _turns(100)
    trimmed = chat_core.trim_history(history, max_messages=4)
    assert trimmed[0] == {"role": "system", "content": "trusted instructions"}
    assert len(trimmed) == 4
    assert [m["content"] for m in trimmed[1:]] == ["m97", "m98", "m99"]


def test_empty_history_is_safe() -> None:
    assert chat_core.trim_history([]) == []


def test_session_request_limit() -> None:
    assert chat_core.session_limit_reached(0) is False
    assert chat_core.session_limit_reached(chat_core.MAX_REQUESTS_PER_SESSION) is True


def test_token_estimate_grows_with_content() -> None:
    small = chat_core.estimate_tokens([{"role": "user", "content": "x" * 40}])
    large = chat_core.estimate_tokens([{"role": "user", "content": "x" * 400}])
    assert large > small


# --- output rendering ----------------------------------------------------


@pytest.mark.parametrize(
    "dangerous",
    [
        "[click me](javascript:alert(1))",
        "[click me](JavaScript:alert(1))",
        "[x](data:text/html;base64,PHNjcmlwdD4=)",
        "[x](vbscript:msgbox)",
    ],
)
def test_dangerous_link_schemes_are_defanged(dangerous: str) -> None:
    result = chat_core.sanitise_markdown_links(dangerous)
    assert "javascript:" not in result.lower()
    assert "data:" not in result.lower()
    assert "vbscript:" not in result.lower()


@pytest.mark.parametrize(
    "safe",
    [
        "[docs](https://example.com/page)",
        "[docs](http://example.com)",
        "[mail](mailto:someone@example.com)",
        "[anchor](#section)",
        "[relative](/docs/page)",
    ],
)
def test_safe_links_are_preserved(safe: str) -> None:
    assert chat_core.sanitise_markdown_links(safe) == safe


def test_ordinary_prose_and_code_blocks_survive() -> None:
    text = "Here is code:\n\n```python\nprint('hi')\n```\n\nAnd **bold** text."
    assert chat_core.sanitise_markdown_links(text) == text


def test_raw_html_is_left_for_the_renderer_to_escape() -> None:
    # The app never enables unsafe_allow_html, so Streamlit escapes this. The
    # helper deliberately does not mangle it.
    text = "<script>alert(1)</script>"
    assert chat_core.sanitise_markdown_links(text) == text


def _app_source() -> str:
    source = pathlib.Path(__file__).resolve().parents[1] / "streamlit_app.py"
    return source.read_text(encoding="utf-8")


def test_app_never_enables_unsafe_html() -> None:
    """The single most important rendering guarantee, asserted against source."""
    body = _app_source()
    assert f"{UNSAFE_HTML_FLAG}=True" not in body
    assert f"{UNSAFE_HTML_FLAG} = True" not in body


def test_every_render_of_model_output_is_sanitised() -> None:
    """Both render paths must sanitise, not just the replay of history.

    A browser check caught this: the streamed reply was rendered straight from
    the provider while replayed history went through the sanitiser, so the same
    content was treated two different ways on the one screen.
    """
    body = _app_source()
    # The streamed response is re-rendered through the sanitiser once complete.
    assert "placeholder.markdown(chat_core.sanitise_markdown_links(response))" in body
    # Replayed history is sanitised too.
    assert 'st.markdown(chat_core.sanitise_markdown_links(message["content"]))' in body
    # Every st.markdown call carrying model or user content goes through it.
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(("st.markdown(", "placeholder.markdown(")):
            assert "sanitise_markdown_links" in stripped, (
                f"unsanitised render: {stripped}"
            )


# --- error handling ------------------------------------------------------


def test_error_message_never_leaks_a_key() -> None:
    exc = RuntimeError(f"Incorrect API key provided: {FAKE_KEY}")
    message = chat_core.safe_error_message(exc)
    assert FAKE_KEY not in message


def test_authentication_error_is_actionable() -> None:
    exc = RuntimeError(f"401 Incorrect API key provided: {FAKE_KEY}")
    assert "rejected" in chat_core.safe_error_message(exc)


def test_rate_limit_error_is_actionable() -> None:
    exc = RuntimeError("429 Rate limit reached for requests")
    assert "rate limiting" in chat_core.safe_error_message(exc)


def test_timeout_error_is_actionable() -> None:
    assert "timed out" in chat_core.safe_error_message(RuntimeError("Request timeout"))


def test_context_length_error_is_actionable() -> None:
    exc = RuntimeError("maximum context length exceeded")
    assert "too long" in chat_core.safe_error_message(exc)


def test_unknown_error_is_bounded_in_length() -> None:
    message = chat_core.safe_error_message(RuntimeError("z" * 5000))
    assert len(message) < 300


def test_empty_error_still_produces_a_message() -> None:
    assert "failed" in chat_core.safe_error_message(RuntimeError(""))
