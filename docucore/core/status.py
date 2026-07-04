"""Project status helpers."""

from __future__ import annotations

from docucore.core.config import RuntimeContext
from docucore.core.filesystem import documentation_paths, list_snapshot_directories


def collect_status(context: RuntimeContext) -> dict[str, object]:
    """Collect the current documentation status for a project."""

    config_exists = context.config_path.exists()
    enabled_plugins = context.config.enabled_plugins if context.config is not None else []
    paths = documentation_paths(context.documentation_root)
    latest_exists = paths["latest_dir"].exists() and any(paths["latest_dir"].iterdir())
    snapshots = list_snapshot_directories(paths["historical_dir"])
    latest_outputs = (
        sorted(path.name for path in paths["latest_dir"].iterdir())
        if paths["latest_dir"].exists()
        else []
    )

    return {
        "project_root": context.project_root,
        "documentation_path": context.documentation_root,
        "config_exists": config_exists,
        "latest_exists": latest_exists,
        "latest_outputs": latest_outputs,
        "last_snapshot": snapshots[0].name if snapshots else None,
        "enabled_plugins": enabled_plugins,
    }
