import os

import streamlit as st
from openai import APIError, AuthenticationError, OpenAI, RateLimitError

from jewelry_assistant import build_messages


st.set_page_config(
    page_title="Star 23 Jewellery Concierge",
    page_icon="✨",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp { background: #fffaf7; color: #2f2424; }
    [data-testid="stHeader"] { background: rgba(255,250,247,.92); }
    .hero {
      padding: 2.5rem 2rem; border-radius: 1.5rem; text-align: center;
      background: linear-gradient(135deg, #402a30, #7b4e57); color: #fffaf7;
      box-shadow: 0 12px 32px rgba(64,42,48,.18); margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0 0 .4rem; font-family: Georgia, serif; font-size: 2.35rem; }
    .hero p { margin: 0; opacity: .9; }
    .trust-note { text-align: center; color: #6d5c5c; font-size: .9rem; }
    div.stButton > button { border-color: #7b4e57; color: #593941; }
    div.stButton > button:hover { border-color: #402a30; color: #402a30; }
    </style>
    <div class="hero">
      <h1>Star 23 Jewellery Concierge</h1>
      <p>Thoughtful help finding, gifting and caring for handmade jewellery.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("About this concierge")
    st.write(
        "Ask for styling, gifting, sizing or jewellery-care guidance. "
        "For current stock, prices and delivery dates, confirm on the shop website."
    )
    st.link_button("Visit Star 23 shop", "https://star23handmadejewellery.com/", use_container_width=True)
    if st.button("Start a new conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def get_api_key() -> str | None:
    """Read a deployed secret first and fall back to a session-only user key."""
    try:
        deployed_key = st.secrets.get("OPENAI_API_KEY")
    except (FileNotFoundError, KeyError):
        deployed_key = None
    return deployed_key or os.getenv("OPENAI_API_KEY")


api_key = get_api_key()
if not api_key:
    with st.expander("Connect the assistant", expanded=True):
        st.caption("Your key is used only for this browser session and is never displayed again.")
        api_key = st.text_input("OpenAI API key", type="password", placeholder="sk-…")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.subheader("How can I help?")
    suggestions = [
        "Help me choose a thoughtful birthday gift",
        "How should I care for handmade jewellery?",
        "Suggest jewellery for a special occasion",
    ]
    columns = st.columns(3)
    for column, suggestion in zip(columns, suggestions):
        if column.button(suggestion, use_container_width=True):
            st.session_state.pending_prompt = suggestion

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.session_state.pop("pending_prompt", None)
typed_prompt = st.chat_input("Ask about gifts, styling, sizing or care…", disabled=not api_key)
prompt = typed_prompt or prompt

if prompt and api_key:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = OpenAI(api_key=api_key)
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=build_messages(st.session_state.messages),
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except AuthenticationError:
        st.error("That API key was not accepted. Please check it and try again.")
    except RateLimitError:
        st.error("The concierge is receiving too many requests. Please wait a moment and try again.")
    except APIError:
        st.error("The concierge is temporarily unavailable. Your message is saved; please try again shortly.")

st.markdown(
    '<p class="trust-note">AI suggestions may be imperfect. Confirm materials, sizing, availability, '
    'pricing and delivery details with Star 23 before purchasing.</p>',
    unsafe_allow_html=True,
)
