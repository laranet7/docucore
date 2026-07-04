"""Snapshot services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from docucore.core.config import RuntimeContext
from docucore.core.filesystem import copy_file, documentation_paths, write_json, write_text
from docucore.core.manifest import build_manifest
from docucore.core.output_plan import resolve_manifest_outputs, resolve_output_artifacts
from docucore.core.writer import load_inventory_outputs
from docucore.exporters.markdown import render_snapshot_markdown
from docucore.models import Manifest, ProjectConfig


@dataclass(slots=True)
class SnapshotArtifacts:
    """Result of snapshot creation."""

    snapshot_id: str
    historical_dir: Path
    latest_dir: Path
    manifest: Manifest


def generate_snapshot_id() -> str:
    """Generate a snapshot identifier using local system time."""

    return datetime.now().astimezone().strftime("%Y.%m.%d_%H.%M.%S")


def create_snapshot_from_outputs(
    context: RuntimeContext,
    config: ProjectConfig,
) -> SnapshotArtifacts:
    """Create a historical snapshot from the current outputs directory."""

    paths = documentation_paths(context.documentation_root)
    artifacts = resolve_output_artifacts(context.documentation_root, config.outputs)
    inventory_json_artifact = next(
        (artifact for artifact in artifacts if artifact.snapshot_name == "inventory.json"),
        None,
    )
    if inventory_json_artifact is None:
        raise FileNotFoundError("Snapshot requires inventory output to be enabled.")
    missing = [artifact.source_path for artifact in artifacts if not artifact.source_path.exists()]
    if missing:
        raise FileNotFoundError(
            "Required outputs not found. Run 'docucore scan' or 'docucore build' first."
        )

    scan_result, inventory = load_inventory_outputs(inventory_json_artifact.source_path)
    snapshot_id = generate_snapshot_id()
    historical_dir = paths["historical_dir"] / snapshot_id
    latest_dir = paths["latest_dir"]
    historical_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)

    for artifact in artifacts:
        copy_file(artifact.source_path, historical_dir / artifact.snapshot_name)
        copy_file(artifact.source_path, latest_dir / artifact.snapshot_name)

    outputs = resolve_manifest_outputs(context.documentation_root, config.outputs)
    manifest = build_manifest(config, snapshot_id=snapshot_id, outputs=outputs)
    snapshot_markdown = render_snapshot_markdown(manifest, scan_result, inventory)

    write_json(historical_dir / "manifest.json", manifest.model_dump(mode="json"))
    write_json(latest_dir / "manifest.json", manifest.model_dump(mode="json"))
    write_text(historical_dir / "snapshot.md", snapshot_markdown)
    write_text(latest_dir / "snapshot.md", snapshot_markdown)

    return SnapshotArtifacts(
        snapshot_id=snapshot_id,
        historical_dir=historical_dir,
        latest_dir=latest_dir,
        manifest=manifest,
    )
