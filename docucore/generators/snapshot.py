"""Snapshot helpers."""

from __future__ import annotations

from docucore.models import Inventory, Manifest, ScanResult


def build_snapshot_summary(
    manifest: Manifest,
    scan_result: ScanResult,
    inventory: Inventory,
) -> dict[str, object]:
    """Prepare compact snapshot summary data."""

    return {
        "snapshot_id": manifest.snapshot_id,
        "project_name": manifest.project_name,
        "generated_at": manifest.generated_at,
        "outputs": manifest.outputs,
        "plugins": manifest.plugins,
        "technologies": inventory.technologies or scan_result.technologies,
        "warnings": inventory.warnings or scan_result.warnings,
    }
