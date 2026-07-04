"""Frontend Markdown generator."""

from __future__ import annotations

from docucore.core.scanner import ScanArtifacts
from docucore.generators.common import get_plugin_data
from docucore.models import Inventory


def build_frontend_markdown(scan_artifacts: ScanArtifacts, inventory: Inventory) -> str:
    """Generate the frontend Markdown document."""

    node_data = get_plugin_data(scan_artifacts, "node")
    frameworks = list(node_data.get("frameworks", []))
    scripts = dict(node_data.get("scripts", {}))
    dependencies = list(node_data.get("dependencies", []))
    structure = list(node_data.get("frontend_structure", []))
    components = list(node_data.get("components", []))
    views = list(node_data.get("views_pages", []))
    routes = list(node_data.get("routes", []))
    stores = list(node_data.get("stores", []))
    composables = list(node_data.get("composables", []))

    framework_summary = ", ".join(frameworks) if frameworks else "sin framework concluyente"

    lines = [
        "# Frontend detectado",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {scan_artifacts.scan_result.project_name}",
        f"- Codigo: {scan_artifacts.scan_result.project_code}",
        "",
        "## Resumen frontend",
        "",
    ]
    if frameworks or components or views:
        lines.append(
            f"- El relevamiento detecta los siguientes frameworks frontend: {framework_summary}."
        )
        lines.append(f"- Componentes detectados: {len(components)}.")
        lines.append(f"- Rutas frontend detectadas: {len(routes)}.")
    else:
        lines.append(
            "- No se cuenta con evidencia suficiente para determinar una capa frontend concluyente."
        )

    lines.extend(["", "## Frameworks detectados", ""])
    if frameworks:
        lines.extend(f"- {item}" for item in frameworks)
    else:
        lines.append("- No se identifican frameworks frontend con evidencia suficiente.")

    lines.extend(["", "## Scripts disponibles", ""])
    if scripts:
        lines.extend(f"- {name}: {command}" for name, command in scripts.items())
    else:
        lines.append("- No se identifican scripts npm.")

    lines.extend(["", "## Dependencias relevantes", ""])
    if dependencies:
        lines.extend(f"- {item}" for item in dependencies[:25])
    else:
        lines.append("- No se identifican dependencias frontend parseables.")

    lines.extend(["", "## Estructura frontend", ""])
    if structure:
        lines.extend(f"- {item}" for item in structure)
    else:
        lines.append("- No se identifica una estructura frontend destacable.")

    lines.extend(["", "## Componentes detectados", ""])
    if components:
        lines.extend(f"- {item}" for item in components[:25])
    else:
        lines.append("- No se identifican componentes con la evidencia disponible.")

    lines.extend(["", "## Vistas o paginas detectadas", ""])
    if views:
        lines.extend(f"- {item}" for item in views[:25])
    else:
        lines.append("- No se identifican vistas o paginas con la evidencia disponible.")

    lines.extend(["", "## Rutas frontend detectadas", ""])
    if routes:
        lines.extend(
            [
                "",
                "| Path | Nombre | Archivo |",
                "| ---- | ------ | ------- |",
            ]
        )
        for route in routes:
            lines.append(
                f"| {route.get('path', '')} | {route.get('name', '')} | {route.get('file', '')} |"
            )
    else:
        lines.append("- No se identifican rutas frontend con la heuristica aplicada.")

    lines.extend(["", "## Stores y composables", ""])
    if stores:
        lines.append(f"- Stores: {', '.join(stores[:20])}")
    if composables:
        lines.append(f"- Composables: {', '.join(composables[:20])}")
    if not any([stores, composables]):
        lines.append("- No se identifican stores ni composables.")

    lines.extend(["", "## Limitaciones", ""])
    lines.append(
        "- La deteccion de rutas frontend usa lectura textual segura y puede omitir "
        "configuraciones dinamicas."
    )
    lines.append(
        "- Esta conclusion debe validarse con revision tecnica manual si la capa frontend "
        "incluye configuraciones dinamicas o generadas."
    )
    return "\n".join(lines).strip() + "\n"
