![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# DocuCore

## What is DocuCore?

DocuCore is a reusable living documentation engine for software projects. It scans repositories, detects structure and technical signals through deterministic plugins, generates Markdown documentation, maintains `historical/` snapshots, and updates a `latest/` view for the most recent run.

## Why DocuCore?

Many projects need technical documentation that stays close to the codebase without introducing external services, hidden heuristics, or mandatory AI dependencies. DocuCore provides a predictable baseline workflow that can be executed locally, in CI, or against external repositories.

## Features

- CLI commands for `init`, `scan`, `build`, `snapshot`, and `status`
- Generic repository scanning with configurable include and exclude paths
- Deterministic plugin architecture for stack-specific detection
- Markdown generation for inventory, architecture, modules, backend, frontend, infrastructure, and snapshots
- Historical snapshots plus a `latest/` documentation view
- External project mode through `--project` and `--output`
- Base mode without AI dependencies or external services

## What DocuCore generates

DocuCore can generate:

- `inventory.json`
- `inventory.md`
- `architecture.md`
- `modules.md`
- `backend.md`
- `frontend.md`
- `infrastructure.md`
- `manifest.json`
- `snapshot.md`

The exact set depends on the configured `outputs` list in `project.config.json`.

## How it works

1. DocuCore resolves the runtime context for the target project and documentation output.
2. The scanner walks the repository while respecting include and exclude rules.
3. Deterministic plugins detect technologies, structure, and technical signals.
4. Generators convert structured plugin data into documentation artifacts.
5. `build` updates `latest/`, writes a manifest, and stores a historical snapshot.

## Installation

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
docucore --help
```

### Linux / Mac

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
docucore --help
```

## Quick start

```bash
docucore init --project-name "Demo Project" --project-code "DEMO"
docucore build
docucore status
```

## Document the current project

If `--project` is not provided, DocuCore uses the current directory as the project being read. If `--output` is not provided, DocuCore writes documentation to `<project>/documentacion`.

```bash
docucore init
docucore scan
docucore build
docucore snapshot
docucore status
```

## Document an external project

DocuCore can read a target repository from one path and write documentation to a separate workspace.

### Windows

```bash
docucore init --project "C:\Projects\SampleProject" --output "C:\DocuCoreWorkspaces\SampleProject\docs" --project-name "Sample Project" --project-code "SAMPLE"

docucore build --project "C:\Projects\SampleProject" --output "C:\DocuCoreWorkspaces\SampleProject\docs"

docucore status --project "C:\Projects\SampleProject" --output "C:\DocuCoreWorkspaces\SampleProject\docs"
```

### Linux / Mac

```bash
docucore init --project "/home/user/projects/SampleProject" --output "/home/user/docucore-workspaces/SampleProject/docs" --project-name "Sample Project" --project-code "SAMPLE"

docucore build --project "/home/user/projects/SampleProject" --output "/home/user/docucore-workspaces/SampleProject/docs"

docucore status --project "/home/user/projects/SampleProject" --output "/home/user/docucore-workspaces/SampleProject/docs"
```

## Generated structure

```text
docs/
├── config/
│   └── project.config.json
├── outputs/
│   ├── inventory/
│   ├── architecture/
│   ├── modules/
│   ├── backend/
│   ├── frontend/
│   └── infrastructure/
├── historical/
│   └── <snapshot_id>/
├── latest/
└── sources/
    └── optional_manual_inputs/
```

## Configuration

DocuCore uses `project.config.json` to define:

- `root_path`: the project being read
- `documentation_path`: the documentation destination being written
- `include_paths`
- `exclude_paths`
- `enabled_plugins`
- `outputs`
- `exporters`
- `ai.enabled`

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for a full explanation.

## Base mode without AI

DocuCore operates in base mode without AI. Initial documentation generation relies on file scanning, deterministic plugins, detection rules, and Markdown generators.

## Future optional AI layer

An optional AI layer may be added later as an enrichment step on top of already generated artifacts. That capability is intentionally out of scope for the current base mode.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the current roadmap and phase structure.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, tests, linting, documentation style, and pull request expectations.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
