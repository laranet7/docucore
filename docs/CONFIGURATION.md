# Configuration

DocuCore uses `project.config.json` to define how a project is scanned and where documentation is written.

## Configuration file

By default, the configuration file is created at:

```text
documentacion/config/project.config.json
```

In external project mode, the configuration file lives inside the configured documentation workspace.

## Key fields

- `project_name`: human-readable project name
- `project_code`: short project code
- `language`: preferred documentation language
- `root_path`: project being read
- `documentation_path`: documentation destination being written
- `include_paths`: paths to traverse during scanning
- `exclude_paths`: paths or directory names to ignore
- `enabled_plugins`: plugin names to execute
- `outputs`: documentation outputs to generate
- `exporters`: exporters to use
- `ai.enabled`: reserved flag for a future optional AI layer

## Example

```json
{
  "project_name": "Sample Project",
  "project_code": "SAMPLE",
  "language": "en",
  "root_path": "C:/Projects/SampleProject",
  "documentation_path": "C:/DocuCoreWorkspaces/SampleProject/docs",
  "include_paths": ["."],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache"
  ],
  "enabled_plugins": ["generic", "python", "node", "dotnet", "docker"],
  "outputs": [
    "inventory",
    "architecture",
    "modules",
    "backend",
    "frontend",
    "infrastructure",
    "snapshot"
  ],
  "exporters": ["markdown"],
  "ai": {
    "enabled": false
  }
}
```

## Path semantics

- `root_path` = project being read
- `documentation_path` = documentation destination being written

Both may be absolute or relative in the file, but DocuCore resolves them to absolute paths internally.

## Runtime precedence

If `--config` is provided, DocuCore loads that file first. If `--project` or `--output` are also provided, the CLI arguments override the corresponding configuration values for the current run.

## Exclusions

DocuCore respects `exclude_paths` during repository traversal. If the documentation destination is inside the project root, DocuCore automatically excludes that folder from scanning so generated outputs do not become scan inputs.

## Output selection

The `outputs` field controls which artifacts are generated. Older configurations that only include `inventory` and `snapshot` remain valid.

## Base mode without AI

The `ai.enabled` flag exists only as a forward-compatible placeholder. The current public baseline does not use AI during scanning or generation.
