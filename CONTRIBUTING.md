# Contributing to DocuCore

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Running tests

```bash
pytest
```

## Running lint

```bash
ruff check .
```

## Branching model

- Use short-lived feature or fix branches.
- Keep `main` stable and ready for release-quality changes.
- Rebase or merge from the target branch as needed to keep validation green.

## Commit style

- Prefer small, reviewable commits.
- Use clear commit messages that describe intent and scope.
- Keep unrelated cleanup out of focused changes whenever possible.

## Pull requests

- Explain the problem being solved.
- Describe the main changes.
- Include validation details such as `pytest` and `ruff check .`.
- Update documentation when behavior, configuration, or outputs change.

## Documentation style

Generated and maintained documentation should be:

- Technical
- Institutional
- Objective
- Evidence-based
- Impersonal

Avoid expressions such as:

- "we observed"
- "I detected"
- "in this workspace it appears"
- "from our review"

Prefer expressions such as:

- "The system includes..."
- "The detected architecture includes..."
- "The available evidence indicates..."
- "The analysis detected..."

When evidence is partial, use prudent language such as:

- "The available evidence suggests..."
- "Indicators of ... were detected."
- "There is not enough evidence to determine..."
- "This conclusion requires manual technical validation."

## Generated files

Generated documentation, local workspaces, personal paths, private sample outputs, and local configuration files must not be committed to the repository.

Do not commit:

- `documentacion/`
- `DocuCoreWorkspaces/`
- `docucore-workspaces/`
- `.env` files
- machine-specific local paths
- client or private project documentation
