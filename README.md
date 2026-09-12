# 💬 Chatbot template

A simple Streamlit app that shows how to build a chatbot using OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Supplying an API key

There are two modes, and the app picks one for you.

- **No key configured.** The app asks each visitor for their own key in a
  password field. That key is used for their browser session only. It is never
  written to disk, logged, or shown back to them.
- **A key configured** in `.streamlit/secrets.toml` or the `OPENAI_API_KEY`
  environment variable. The app uses it and stops asking. Copy `.env.example`
  for the variable name.

A configured key means every visitor spends your credit, so read the limits
below before exposing such a deployment publicly.

### Safety and cost controls

These live in `chat_core.py`, away from the interface, so they can be tested
without a UI or a paid API call. `tests/test_chat_core.py` covers them.

| Control | Default | Why |
|---|---|---|
| Input length | 4,000 characters | Rejects an oversized prompt before it costs anything |
| Conversation history sent | 20 messages | Without a bound, cost grows with the square of the conversation and eventually exceeds the context window |
| Output tokens | 800 | Caps the reply, and so the billed completion |
| Requests per session | 50 | Bounds what one visitor can spend |
| Request timeout | 60 seconds | A stalled provider cannot hold a session open |
| Retries | 2 | Bounds how many times one failure is billed |

A leading system message is preserved when history is trimmed, so trusted
instructions are never dropped in favour of recent chat.

These bound the number and size of requests. They are not a monetary cap, and
the token figures reported in the code are character-count approximations
rather than the provider's own tokeniser.

### Rendering

Messages render through Streamlit's default Markdown handling, which escapes raw
HTML. `unsafe_allow_html` is never enabled, and a test asserts that against the
source. Links whose scheme is not `http`, `https` or `mailto` are reduced to
their visible text before rendering.

### Running the tests

```
$ pip install -r requirements-dev.txt
$ python -m pytest tests/ -q
```

The suite needs neither Streamlit nor the OpenAI library, and never calls a
provider.
