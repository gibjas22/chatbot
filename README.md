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

3. Run the tests

   ```
   $ python -m unittest discover -s tests -t .
   ```

### Ogenic God Mode toolkit

This repository ships the Ogenic God Mode toolkit: Claude Code skills, slash
commands and CI checks that turn a coding session into a repeatable workflow
of Frame, Plan, Build, Verify, Ship.

Start a Claude Code session here and run `/god-mode`, or go straight to a
stage with `/build`, `/secure` or `/ship`.

Install it into another project, or into your user config for every project:

```
$ ./tools/ogenic/install.sh --target ../my-other-project
$ ./tools/ogenic/install.sh --user
```

Full documentation is in [docs/OGENIC_GOD_MODE.md](docs/OGENIC_GOD_MODE.md).
