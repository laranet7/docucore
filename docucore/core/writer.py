"""Writers for DocuCore outputs."""

from __future__ import annotations

from pathlib import Path

from docucore.core.config import RuntimeContext
from docucore.core.constants import MARKDOWN_OUTPUT_NAMES
from docucore.core.filesystem import documentation_paths, read_json, write_json, write_text
from docucore.core.output_plan import normalize_output_names
from docucore.core.scanner import ScanArtifacts
from docucore.exporters.markdown import render_inventory_markdown
from docucore.generators.architecture import build_architecture_markdown
from docucore.generators.backend import build_backend_markdown
from docucore.generators.frontend import build_frontend_markdown
from docucore.generators.infrastructure import build_infrastructure_markdown
from docucore.generators.inventory import build_inventory
from docucore.generators.modules import build_modules_markdown
from docucore.models import Inventory, ProjectConfig, ScanResult


def build_inventory_payload(
    scan_artifacts: ScanArtifacts,
    inventory: Inventory,
) -> dict[str, object]:
    """Create the persisted payload for inventory.json."""

    return {
        "project_name": scan_artifacts.scan_result.project_name,
        "project_code": scan_artifacts.scan_result.project_code,
        "generated_at": scan_artifacts.scan_result.generated_at,
        "scan_result": scan_artifacts.scan_result.model_dump(mode="json"),
        "inventory": inventory.model_dump(mode="json"),
    }


def write_inventory_outputs(
    context: RuntimeContext,
    config: ProjectConfig,
    scan_artifacts: ScanArtifacts,
) -> tuple[Inventory, dict[str, Path]]:
    """Write configured documentation outputs and return generated paths."""

    inventory = build_inventory(scan_artifacts)
    paths = documentation_paths(context.documentation_root)
    written_paths: dict[str, Path] = {}
    enabled_outputs = normalize_output_names(config.outputs)

    if "inventory" in enabled_outputs:
        inventory_dir = paths["inventory_dir"]
        inventory_json = inventory_dir / "inventory.json"
        inventory_md = inventory_dir / "inventory.md"
        write_json(inventory_json, build_inventory_payload(scan_artifacts, inventory))
        write_text(inventory_md, render_inventory_markdown(scan_artifacts.scan_result, inventory))
        written_paths["inventory.json"] = inventory_json
        written_paths["inventory.md"] = inventory_md

    markdown_builders = {
        "architecture": build_architecture_markdown,
        "modules": build_modules_markdown,
        "backend": build_backend_markdown,
        "frontend": build_frontend_markdown,
        "infrastructure": build_infrastructure_markdown,
    }
    for output_name in MARKDOWN_OUTPUT_NAMES:
        if output_name not in enabled_outputs:
            continue
        output_path = paths["outputs_dir"] / output_name / f"{output_name}.md"
        content = markdown_builders[output_name](scan_artifacts, inventory)
        write_text(output_path, content)
        written_paths[f"{output_name}.md"] = output_path

    return inventory, written_paths


def load_inventory_outputs(inventory_json_path: Path) -> tuple[ScanResult, Inventory]:
    """Load a previously generated inventory payload."""

    payload = read_json(inventory_json_path)
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid inventory payload at {inventory_json_path}")
    scan_result = ScanResult.model_validate(payload["scan_result"])
    inventory = Inventory.model_validate(payload["inventory"])
    return scan_result, inventory
