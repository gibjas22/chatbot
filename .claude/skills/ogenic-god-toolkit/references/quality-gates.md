# Verification commands by stack

Run what the project actually has. Never invent a tool that is not installed.

## Python

```bash
pytest -q                      # tests
ruff check .                   # lint
ruff format --check .          # formatting
mypy .                         # types, if configured
pip-audit                      # dependency vulnerabilities
python -c "import streamlit_app"   # import smoke test
```

## Node and TypeScript

```bash
npm test
npx eslint .
npx prettier --check .
npx tsc --noEmit
npm audit --omit=dev
```

## Go

```bash
go test ./...
go vet ./...
gofmt -l .
staticcheck ./...
```

## Rust

```bash
cargo test
cargo clippy -- -D warnings
cargo fmt --check
```

## Discovering what exists

```bash
cat package.json 2>/dev/null | grep -A15 '"scripts"'
cat Makefile 2>/dev/null | grep -E '^[a-z-]+:'
cat pyproject.toml tox.ini setup.cfg 2>/dev/null | head -40
ls .github/workflows/ 2>/dev/null && cat .github/workflows/*.y*ml 2>/dev/null | grep -E 'run:' | head -20
```

The CI workflow is the most reliable source of truth for what must pass.

## This project

Streamlit and OpenAI, Python. There is no test suite yet. Minimum gate:

```bash
python -m py_compile streamlit_app.py
pip install -r requirements.txt
streamlit run streamlit_app.py --server.headless true &
sleep 5 && curl -sf http://localhost:8501 >/dev/null && echo "app serves" ; kill %1
```

If a change adds logic worth testing, add `pytest` and a `tests/` directory rather than shipping
untested behaviour.
