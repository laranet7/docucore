"""Shared constants for DocuCore."""

from pathlib import Path

APP_NAME = "docucore"
DEFAULT_DOCUMENTATION_PATH = "documentacion"
CONFIG_FILE_NAME = "project.config.json"
CONFIG_RELATIVE_PATH = Path(DEFAULT_DOCUMENTATION_PATH) / "config" / CONFIG_FILE_NAME

DEFAULT_EXCLUDE_PATHS = [
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
    ".ruff_cache",
]
DEFAULT_ENABLED_PLUGINS = ["generic", "python", "node", "dotnet", "docker"]
DEFAULT_OUTPUTS = [
    "inventory",
    "architecture",
    "modules",
    "backend",
    "frontend",
    "infrastructure",
    "snapshot",
]
DEFAULT_EXPORTERS = ["markdown"]

DOCUMENTATION_SUBDIRECTORIES = [
    "config",
    "outputs",
    "outputs/inventory",
    "outputs/architecture",
    "outputs/modules",
    "outputs/backend",
    "outputs/frontend",
    "outputs/infrastructure",
    "outputs/traceability",
    "outputs/audits",
    "outputs/integral",
    "outputs/final",
    "historical",
    "latest",
    "sources",
    "sources/optional_manual_inputs",
]

RELEVANT_FILENAMES = {
    "README.md",
    "docker-compose.yml",
    "docker-compose.yaml",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    ".gitlab-ci.yml",
    "Dockerfile",
}
RELEVANT_GLOBS = ["*.csproj", "*.sln"]

MARKDOWN_OUTPUT_NAMES = [
    "architecture",
    "modules",
    "backend",
    "frontend",
    "infrastructure",
]
