# Contributing to Vyse

Thanks for your interest. Vyse is a portfolio project first, but PRs that improve detection accuracy, add integrations, or polish the UI are welcome.

## Development setup

```bash
# Pre-commit hooks (ruff + black + prettier)
pip install pre-commit
pre-commit install

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q

# Dashboard
cd ../dashboard
npm install
npm run typecheck
npm run build
```

## Conventions

- **Python:** ruff for linting, black for formatting (100-col), type hints required for public functions.
- **TypeScript:** strict mode, prefer Server Components, use shadcn primitives over Material/Chakra.
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- **Tests:** every detector/agent change needs a unit test; every new endpoint an integration test.

## Filing issues

Please include:

- Vyse version / commit SHA.
- Hardware tier (DEV / EDGE / SMB / PROD — see PRD §19).
- Minimal repro (a 30-second video sample is gold).
- Expected vs. actual behavior.

## License

By contributing you agree your contributions are licensed under [MIT](../LICENSE).
