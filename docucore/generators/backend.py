"""Backend Markdown generator."""

from __future__ import annotations

from docucore.core.scanner import ScanArtifacts
from docucore.generators.common import get_plugin_data
from docucore.models import Inventory


def build_backend_markdown(scan_artifacts: ScanArtifacts, inventory: Inventory) -> str:
    """Generate the backend Markdown document."""

    python_data = get_plugin_data(scan_artifacts, "python")
    frameworks = []
    if python_data.get("fastapi_detected"):
        frameworks.append("FastAPI")
    if "python" in inventory.technologies:
        frameworks.append("Python")

    dependencies = list(python_data.get("dependencies", []))
    backend_dirs = list(python_data.get("backend_structure_dirs", []))
    endpoints = list(python_data.get("endpoints", []))
    models = list(python_data.get("models", []))
    schemas = list(python_data.get("schemas", []))
    services = list(python_data.get("services", []))

    framework_summary = ", ".join(frameworks) if frameworks else "sin framework concluyente"
    backend_dirs_summary = ", ".join(backend_dirs) if backend_dirs else "sin datos"

    lines = [
        "# Backend detectado",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {scan_artifacts.scan_result.project_name}",
        f"- Codigo: {scan_artifacts.scan_result.project_code}",
        "",
        "## Resumen backend",
        "",
    ]
    if frameworks or backend_dirs or endpoints:
        lines.append(
            f"- El relevamiento detecta los siguientes frameworks backend: {framework_summary}."
        )
        lines.append(f"- La estructura backend identificada incluye: {backend_dirs_summary}.")
        lines.append(f"- Endpoints detectados: {len(endpoints)}.")
    else:
        lines.append(
            "- No se cuenta con evidencia suficiente para determinar una capa backend concluyente."
        )

    lines.extend(["", "## Frameworks detectados", ""])
    if frameworks:
        lines.extend(f"- {item}" for item in frameworks)
    else:
        lines.append("- No se identifican frameworks backend con evidencia suficiente.")

    lines.extend(["", "## Estructura backend", ""])
    if backend_dirs:
        lines.extend(f"- {item}" for item in backend_dirs)
    else:
        lines.append("- No se identifica una estructura backend destacable.")

    lines.extend(["", "## Dependencias relevantes", ""])
    if dependencies:
        lines.extend(f"- {item}" for item in dependencies[:20])
    else:
        lines.append("- No se identifican dependencias backend parseables.")

    lines.extend(["", "## Endpoints detectados", ""])
    if endpoints:
        lines.extend(
            [
                "",
                "| Metodo | Path | Handler | Archivo |",
                "| ------ | ---- | ------- | ------- |",
            ]
        )
        for endpoint in endpoints:
            lines.append(
                f"| {endpoint.get('method', '')} | {endpoint.get('path', '')} | "
                f"{endpoint.get('handler', '')} | {endpoint.get('file', '')} |"
            )
    else:
        lines.append("- No se detectaron endpoints.")

    lines.extend(["", "## Modelos, schemas y servicios detectados", ""])
    if models:
        lines.append(f"- Models: {', '.join(models)}")
    if schemas:
        lines.append(f"- Schemas: {', '.join(schemas)}")
    if services:
        lines.append(f"- Services: {', '.join(services)}")
    if not any([models, schemas, services]):
        lines.append(
            "- No se identifican models, schemas o services mediante la heuristica aplicada."
        )

    lines.extend(["", "## Limitaciones", ""])
    lines.append(
        "- La deteccion de endpoints usa heuristicas por decoradores y no reemplaza un "
        "parser completo."
    )
    lines.append(
        "- No se cuenta con evidencia suficiente para determinar cobertura funcional completa "
        "sin revision tecnica manual."
    )
    return "\n".join(lines).strip() + "\n"
