"""Helpers to resolve configured documentation outputs."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from docucore.core.constants import DEFAULT_OUTPUTS, MARKDOWN_OUTPUT_NAMES
from docucore.core.filesystem import documentation_paths

SUPPORTED_OUTPUTS = [*DEFAULT_OUTPUTS]


@dataclass(slots=True)
class OutputArtifact:
    """A generated output file and the name used in latest/historical snapshots."""

    output_name: str
    source_path: Path
    snapshot_name: str


def normalize_output_names(output_names: Iterable[str]) -> list[str]:
    """Return configured outputs in stable order, ignoring unsupported duplicates."""

    requested = set(output_names)
    return [name for name in SUPPORTED_OUTPUTS if name in requested]


def resolve_output_artifacts(
    documentation_root: Path,
    output_names: Iterable[str],
) -> list[OutputArtifact]:
    """Resolve output files generated for the configured outputs."""

    paths = documentation_paths(documentation_root)
    artifacts: list[OutputArtifact] = []
    for output_name in normalize_output_names(output_names):
        if output_name == "inventory":
            artifacts.extend(
                [
                    OutputArtifact(
                        output_name="inventory",
                        source_path=paths["inventory_dir"] / "inventory.json",
                        snapshot_name="inventory.json",
                    ),
                    OutputArtifact(
                        output_name="inventory",
                        source_path=paths["inventory_dir"] / "inventory.md",
                        snapshot_name="inventory.md",
                    ),
                ]
            )
        elif output_name in MARKDOWN_OUTPUT_NAMES:
            artifacts.append(
                OutputArtifact(
                    output_name=output_name,
                    source_path=paths["outputs_dir"] / output_name / f"{output_name}.md",
                    snapshot_name=f"{output_name}.md",
                )
            )
    return artifacts


def resolve_manifest_outputs(documentation_root: Path, output_names: Iterable[str]) -> list[str]:
    """Resolve manifest output filenames for the configured outputs."""

    artifact_names = [
        artifact.snapshot_name
        for artifact in resolve_output_artifacts(documentation_root, output_names)
    ]
    return [*artifact_names, "manifest.json", "snapshot.md"]
