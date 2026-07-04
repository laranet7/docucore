"""Manifest generation helpers."""

from __future__ import annotations

from datetime import datetime

from docucore import __version__
from docucore.models import Manifest, ProjectConfig


def build_manifest(config: ProjectConfig, snapshot_id: str, outputs: list[str]) -> Manifest:
    """Build a manifest model for the current latest/snapshot state."""

    return Manifest(
        project_name=config.project_name,
        project_code=config.project_code,
        generated_at=datetime.now().astimezone().isoformat(),
        docucore_version=__version__,
        snapshot_id=snapshot_id,
        outputs=outputs,
        plugins=list(config.enabled_plugins),
    )

