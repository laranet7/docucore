"""Inventory generator."""

from __future__ import annotations

from docucore.core.scanner import ScanArtifacts
from docucore.models import Inventory, InventorySummary


def build_inventory(scan_artifacts: ScanArtifacts) -> Inventory:
    """Build an inventory model from scan artifacts."""

    generic_result = next(
        (plugin for plugin in scan_artifacts.scan_result.plugins if plugin.name == "generic"),
        None,
    )
    relevant_files = []
    if generic_result is not None:
        relevant_files = list(generic_result.data.get("relevant_files", []))

    modules = [
        {
            "plugin": plugin.name,
            "detected": plugin.detected,
            "technologies": plugin.technologies,
            "data": plugin.data,
        }
        for plugin in scan_artifacts.scan_result.plugins
    ]

    summary = InventorySummary(
        total_files=scan_artifacts.scan_result.files_scanned,
        total_directories=scan_artifacts.scan_result.directories_scanned,
        detected_plugins=sum(1 for plugin in scan_artifacts.scan_result.plugins if plugin.detected),
        relevant_files=relevant_files,
    )

    return Inventory(
        summary=summary,
        technologies=scan_artifacts.scan_result.technologies,
        modules=modules,
        files=scan_artifacts.files,
        plugins=scan_artifacts.scan_result.plugins,
        findings=scan_artifacts.scan_result.findings,
        warnings=scan_artifacts.scan_result.warnings,
    )

