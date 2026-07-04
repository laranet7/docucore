"""Configuration services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from docucore.core.constants import (
    DEFAULT_DOCUMENTATION_PATH,
    DEFAULT_ENABLED_PLUGINS,
    DEFAULT_EXCLUDE_PATHS,
    DEFAULT_EXPORTERS,
    DEFAULT_OUTPUTS,
)
from docucore.core.filesystem import (
    documentation_paths,
    ensure_documentation_structure,
    read_json,
    write_json,
)
from docucore.models import ProjectConfig


@dataclass(slots=True)
class RuntimeContext:
    """Resolved runtime paths and effective configuration."""

    project_root: Path
    documentation_root: Path
    config_path: Path
    config: ProjectConfig | None = None


def build_default_config(
    project_root: Path | None = None,
    documentation_root: Path | None = None,
    project_name: str = "Unnamed Project",
    project_code: str = "UNNAMED",
) -> ProjectConfig:
    """Build the default project configuration."""

    root_path = project_root.resolve().as_posix() if project_root is not None else "."
    documentation_path = (
        documentation_root.resolve().as_posix()
        if documentation_root is not None
        else DEFAULT_DOCUMENTATION_PATH
    )

    return ProjectConfig(
        project_name=project_name,
        project_code=project_code,
        language="es",
        root_path=root_path,
        documentation_path=documentation_path,
        include_paths=["."],
        exclude_paths=list(DEFAULT_EXCLUDE_PATHS),
        enabled_plugins=list(DEFAULT_ENABLED_PLUGINS),
        outputs=list(DEFAULT_OUTPUTS),
        exporters=list(DEFAULT_EXPORTERS),
    )


def save_project_config(config_path: Path, config: ProjectConfig, force: bool = False) -> Path:
    """Persist a project configuration to disk."""

    if config_path.exists() and not force:
        raise FileExistsError(f"Configuration already exists at {config_path}")
    write_json(config_path, config.model_dump(mode="json"))
    return config_path


def load_project_config(config_path: Path) -> ProjectConfig:
    """Load and validate project configuration."""

    try:
        raw_data = read_json(config_path)
        return ProjectConfig.model_validate(raw_data)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Configuration file not found: {config_path}") from exc
    except ValidationError as exc:
        raise ValueError(f"Invalid configuration file: {config_path}") from exc


def validate_project_root(project_root: Path) -> Path:
    """Validate that a project root exists and is a directory."""

    resolved = project_root.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Project path does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {resolved}")
    return resolved


def resolve_output_root(output_root: Path) -> Path:
    """Resolve an output directory path without requiring it to exist."""

    return output_root.expanduser().resolve()


def project_root_from_config_path(config_path: Path) -> Path:
    """Infer a legacy project root from a configuration file path."""

    resolved = config_path.resolve()
    if len(resolved.parents) < 3:
        return resolved.parent
    return resolved.parents[2]


def resolve_configured_path(raw_path: str, *, base_root: Path) -> Path:
    """Resolve a configured path using the provided base root when relative."""

    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (base_root / candidate).resolve()


def resolve_runtime_context(
    project: Path | None = None,
    output: Path | None = None,
    config: Path | None = None,
    *,
    require_config: bool,
) -> RuntimeContext:
    """Resolve the effective project, output and configuration paths for a command."""

    config_path = config.expanduser().resolve() if config is not None else None
    loaded_config: ProjectConfig | None = None
    configured_project_root: Path | None = None
    configured_documentation_root: Path | None = None

    if config_path is not None and config_path.exists():
        loaded_config = load_project_config(config_path)
        legacy_project_root = project_root_from_config_path(config_path)
        configured_project_root = resolve_configured_path(
            loaded_config.root_path,
            base_root=legacy_project_root,
        )
        configured_documentation_root = resolve_configured_path(
            loaded_config.documentation_path,
            base_root=configured_project_root,
        )
    elif config_path is not None and require_config:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    project_root = (
        validate_project_root(project)
        if project is not None
        else configured_project_root or Path.cwd().resolve()
    )
    if project is None:
        project_root = validate_project_root(project_root)

    if output is not None:
        documentation_root = resolve_output_root(output)
    elif configured_documentation_root is not None:
        documentation_root = configured_documentation_root
    elif config_path is not None:
        documentation_root = config_path.parent.parent.resolve()
    else:
        documentation_root = (project_root / DEFAULT_DOCUMENTATION_PATH).resolve()

    if config_path is None:
        config_path = documentation_paths(documentation_root)["config_path"]

    if loaded_config is None and config_path.exists():
        loaded_config = load_project_config(config_path)
    elif loaded_config is None and require_config:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    effective_config = None
    if loaded_config is not None:
        effective_config = loaded_config.model_copy(
            update={
                "root_path": project_root.as_posix(),
                "documentation_path": documentation_root.as_posix(),
            }
        )

    return RuntimeContext(
        project_root=project_root,
        documentation_root=documentation_root,
        config_path=config_path,
        config=effective_config,
    )


def initialize_project(
    project_root: Path,
    documentation_root: Path,
    project_name: str = "Unnamed Project",
    project_code: str = "UNNAMED",
    force: bool = False,
) -> dict[str, object]:
    """Create documentation structure and bootstrap configuration."""

    project_root = validate_project_root(project_root)
    documentation_root = resolve_output_root(documentation_root)
    created_directories = ensure_documentation_structure(documentation_root)
    config = build_default_config(
        project_root=project_root,
        documentation_root=documentation_root,
        project_name=project_name,
        project_code=project_code,
    )
    config_path = documentation_paths(documentation_root)["config_path"]

    config_existed = config_path.exists()
    if not config_existed or force:
        save_project_config(config_path, config, force=True)
    else:
        config = load_project_config(config_path)

    return {
        "config": config,
        "config_path": config_path,
        "created_directories": created_directories,
        "config_created": not config_existed,
        "config_overwritten": config_existed and force,
    }
