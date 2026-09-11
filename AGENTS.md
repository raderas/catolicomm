# AGENTS.md

## Setup commands:
- Create/Activate venv: `python3 -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Apply migrations: `python manage.py migrate`
- Run tests: `python manage.py test`

## Code style
- After python edits, run `pre-commit run ruff-check --all-files`  and `pre-commit run ruff-format --all-files`. Fix reported issues. Match existing typing/lint patterns in the same module.
- Do not edit generated migration files by hand.
- User facing copy is in Spanish.
