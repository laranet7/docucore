"""Markdown exporters."""

from __future__ import annotations

from docucore.models import Inventory, Manifest, ScanResult


def render_inventory_markdown(scan_result: ScanResult, inventory: Inventory) -> str:
    """Render the inventory Markdown output."""

    generic_data = next(
        (plugin.data for plugin in inventory.plugins if plugin.name == "generic"),
        {},
    )
    main_directories = generic_data.get("main_directories", [])
    relevant_files = generic_data.get("relevant_files", [])

    lines = [
        "# Inventario tecnico",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {scan_result.project_name}",
        f"- Codigo: {scan_result.project_code}",
        f"- Fecha de generacion: {scan_result.generated_at}",
        "",
        "## Resumen",
        "",
        (
            "- El relevamiento tecnico se basa en evidencia detectada automaticamente "
            "en el repositorio."
        ),
        f"- Archivos analizados: {inventory.summary.total_files}",
        f"- Directorios analizados: {inventory.summary.total_directories}",
        f"- Plugins con deteccion activa: {inventory.summary.detected_plugins}",
        "",
        "## Tecnologias detectadas",
        "",
    ]

    if inventory.technologies:
        lines.extend(f"- {technology}" for technology in inventory.technologies)
    else:
        lines.append("- No se detectaron tecnologias.")

    lines.extend(["", "## Estructura principal", ""])
    if main_directories:
        lines.extend(f"- {directory}" for directory in main_directories)
    else:
        lines.append("- No se detectaron directorios principales.")

    lines.extend(["", "## Hallazgos por plugin", ""])
    for plugin in inventory.plugins:
        lines.append(f"### {plugin.name}")
        if plugin.findings:
            lines.extend([""] + [f"- {finding}" for finding in plugin.findings])
        else:
            lines.extend(["", "- No se identifican hallazgos relevantes para este plugin."])
        lines.append("")

    lines.extend(["## Advertencias", ""])
    if inventory.warnings:
        lines.extend(f"- {warning}" for warning in inventory.warnings)
    else:
        lines.append("- Sin advertencias.")

    lines.extend(["", "## Archivos relevantes", ""])
    if relevant_files:
        lines.extend(f"- {path}" for path in relevant_files)
    else:
        lines.append("- No se detectaron archivos relevantes.")

    return "\n".join(lines).strip() + "\n"


def render_snapshot_markdown(
    manifest: Manifest,
    scan_result: ScanResult,
    inventory: Inventory,
) -> str:
    """Render the snapshot Markdown output."""

    lines = [
        "# Snapshot documental",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {manifest.project_name}",
        f"- Codigo: {manifest.project_code}",
        "",
        "## Snapshot",
        "",
        f"- ID: {manifest.snapshot_id}",
        f"- Fecha de generacion: {manifest.generated_at}",
        "",
        "## Outputs incluidos",
        "",
    ]
    lines.extend(f"- {output}" for output in manifest.outputs)
    lines.extend(["", "## Plugins ejecutados", ""])
    if manifest.plugins:
        lines.extend(f"- {plugin}" for plugin in manifest.plugins)
    else:
        lines.append("- No se ejecutaron plugins.")

    lines.extend(["", "## Resumen tecnico", ""])
    if inventory.technologies:
        technologies = ", ".join(inventory.technologies)
        lines.append(f"- La evidencia tecnica disponible indica uso de: {technologies}")
    else:
        lines.append(
            "- No se cuenta con evidencia suficiente para determinar tecnologias "
            "predominantes."
        )
    lines.append(f"- Archivos analizados: {scan_result.files_scanned}")
    lines.append(f"- Directorios analizados: {scan_result.directories_scanned}")

    return "\n".join(lines).strip() + "\n"
