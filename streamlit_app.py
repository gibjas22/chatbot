import os

import streamlit as st
from openai import OpenAI

import chat_core

MODEL = "gpt-3.5-turbo"

st.title("💬 Chatbot")
st.write(
    "A simple chatbot built on OpenAI's GPT-3.5 model. "
    "It is rate limited and length limited so a long conversation cannot run up "
    "an unbounded bill. Learn how to build it by "
    "[following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)


def _operator_key() -> str | None:
    """Read a deployment-wide key, if the operator configured one.

    `st.secrets` raises rather than returning None when no secrets file exists,
    and the exception type has changed across Streamlit versions, so the guard
    is deliberately broad. Missing configuration is a normal state here, not an
    error: the app falls back to asking the visitor for their own key. Letting
    any exception escape would take the whole page down over an absent file.
    """
    try:
        value = st.secrets.get("OPENAI_API_KEY")
    except Exception:  # noqa: BLE001 - see above; the raised type varies by version
        value = None
    return value or None


operator_key = _operator_key()
environment_key = os.environ.get("OPENAI_API_KEY")

# Only ask the visitor for a key when the deployment has not supplied one.
user_key = None
if not (operator_key or environment_key):
    user_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help=(
            "Used only for this browser session. It is never written to disk, "
            "logged, or shown back to you."
        ),
    )

api_key, key_source = chat_core.resolve_api_key(operator_key, environment_key, user_key)

if not api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# Bounded retries and an explicit timeout, so a stalled provider cannot hold a
# session open indefinitely or silently multiply the number of billed calls.
client = OpenAI(
    api_key=api_key,
    timeout=chat_core.REQUEST_TIMEOUT_SECONDS,
    max_retries=chat_core.MAX_RETRIES,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "request_count" not in st.session_state:
    st.session_state.request_count = 0

# Session state is per browser session, so one visitor's key and history are
# never visible to another. It is not an authorisation boundary and is not
# treated as one.
with st.sidebar:
    st.caption(f"API key source: {key_source}")
    st.caption(
        f"Requests used: {st.session_state.request_count} "
        f"of {chat_core.MAX_REQUESTS_PER_SESSION}"
    )
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.request_count = 0
        st.rerun()

# Rendered with Streamlit's default Markdown handling, which escapes raw HTML.
# Raw-HTML rendering is deliberately never enabled anywhere in this file, and a
# test in tests/test_chat_core.py asserts that against this source.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(chat_core.sanitise_markdown_links(message["content"]))

if prompt := st.chat_input("What is up?"):
    validation = chat_core.validate_user_input(prompt)
    if not validation.ok:
        st.warning(validation.message)
        st.stop()

    if chat_core.session_limit_reached(st.session_state.request_count):
        st.warning(
            f"This session has used its limit of "
            f"{chat_core.MAX_REQUESTS_PER_SESSION} requests. "
            "Clear the conversation in the sidebar to start again."
        )
        st.stop()

    # The prompt is shown at once but is not written to history until the turn
    # completes. Appending first leaves an orphaned user message behind whenever
    # the provider call fails, and trim_history then resends that orphan on every
    # later turn: two user messages in a row, for a turn the model never answered.
    with st.chat_message("user"):
        st.markdown(chat_core.sanitise_markdown_links(prompt))

    # Only the most recent turns are sent. Without this the whole history is
    # resent every turn, so cost grows with the square of the conversation.
    outbound = chat_core.trim_history(
        st.session_state.messages + [{"role": "user", "content": prompt}]
    )

    try:
        st.session_state.request_count += 1
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": m["role"], "content": m["content"]} for m in outbound],
            max_tokens=chat_core.MAX_OUTPUT_TOKENS,
            stream=True,
        )
        with st.chat_message("assistant"):
            # Stream into a placeholder for the live typing effect, then replace
            # it with the sanitised text once complete. Without the second step
            # the streaming path would render unsanitised model output, while
            # replayed history got the sanitiser: the same content treated two
            # different ways, with only the framework's own escaping in between.
            placeholder = st.empty()
            with placeholder.container():
                response = st.write_stream(stream)
            placeholder.markdown(chat_core.sanitise_markdown_links(response))
    except Exception as exc:  # noqa: BLE001 - any provider error must stay off the page
        st.error(chat_core.safe_error_message(exc))
        st.stop()

    # Both halves of the turn are committed together, once there is something to
    # commit. Either the exchange is in history or neither side of it is.
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
