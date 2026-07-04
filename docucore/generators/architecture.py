"""Architecture Markdown generator."""

from __future__ import annotations

from docucore.core.scanner import ScanArtifacts
from docucore.generators.common import get_plugin_data
from docucore.models import Inventory


def build_architecture_markdown(scan_artifacts: ScanArtifacts, inventory: Inventory) -> str:
    """Generate the architecture Markdown document."""

    generic_data = get_plugin_data(scan_artifacts, "generic")
    python_data = get_plugin_data(scan_artifacts, "python")
    node_data = get_plugin_data(scan_artifacts, "node")
    docker_data = get_plugin_data(scan_artifacts, "docker")

    layers: list[str] = []
    summary: list[str] = []
    backend_notes: list[str] = []
    frontend_notes: list[str] = []
    infrastructure_notes: list[str] = []
    integrations: list[str] = []
    limitations = [
        "La arquitectura se documenta solo a partir de evidencia detectada en archivos y carpetas.",
        "No se infieren relaciones internas que no esten visibles en el repositorio.",
    ]

    main_directories = generic_data.get("main_directories", [])
    if "backend" in main_directories and "frontend" in main_directories:
        summary.append(
            "La arquitectura detectada incluye una separacion backend/frontend a partir de las "
            "carpetas backend y frontend."
        )
        layers.extend(["backend", "frontend"])

    if python_data.get("fastapi_detected"):
        summary.append("Se identifican indicadores de FastAPI en la capa backend Python.")
        backend_notes.append(
            "La evidencia tecnica disponible indica uso de FastAPI mediante imports, "
            "APIRouter o uvicorn."
        )
        if "backend" not in layers:
            layers.append("backend")
    elif python_data.get("python_directories"):
        backend_notes.append(
            "Se identifican directorios Python compatibles con una estructura backend."
        )
        if "backend" not in layers:
            layers.append("backend")

    frameworks = node_data.get("frameworks", [])
    if frameworks:
        summary.append(
            "La evidencia tecnica disponible indica uso de "
            f"{', '.join(frameworks)} en la capa frontend."
        )
        frontend_notes.append(
            f"Se identifican frameworks frontend: {', '.join(frameworks)}."
        )
        if "frontend" not in layers:
            layers.append("frontend")

    if docker_data.get("compose_file"):
        summary.append("Se detecta orquestacion local mediante docker-compose.")
        infrastructure_notes.append(
            "La infraestructura declarativa incluye docker-compose con servicios definidos."
        )
        if "infrastructure" not in layers:
            layers.append("infrastructure")
    elif docker_data.get("dockerfiles"):
        infrastructure_notes.append(
            "Se identifican Dockerfiles asociados a la infraestructura del proyecto."
        )
        if "infrastructure" not in layers:
            layers.append("infrastructure")

    github_workflows = generic_data.get("github_workflow_files", [])
    gitlab_ci = generic_data.get("gitlab_ci_files", [])
    if github_workflows:
        integrations.append("Se identifican workflows versionados de GitHub Actions.")
    if gitlab_ci:
        integrations.append("Se identifica configuracion de GitLab CI mediante .gitlab-ci.yml.")

    if not summary:
        summary.append(
            "No se cuenta con evidencia suficiente para determinar una arquitectura tecnica clara."
        )
        limitations.append(
            "Esta conclusion debe validarse con revision tecnica manual si se requiere "
            "mayor precision."
        )

    technologies = ", ".join(inventory.technologies) if inventory.technologies else "sin datos"

    lines = [
        "# Arquitectura tecnica detectada",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {scan_artifacts.scan_result.project_name}",
        f"- Codigo: {scan_artifacts.scan_result.project_code}",
        f"- Fecha de generacion: {scan_artifacts.scan_result.generated_at}",
        "",
        "## Resumen de arquitectura",
        "",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend(["", "## Capas detectadas", ""])
    if layers:
        lines.extend(f"- {layer}" for layer in layers)
    else:
        lines.append("- No se detectaron capas diferenciadas.")

    lines.extend(["", "## Backend", ""])
    if backend_notes:
        lines.extend(f"- {item}" for item in backend_notes)
    else:
        lines.append(
            "- No se cuenta con evidencia suficiente para determinar una capa backend concluyente."
        )

    lines.extend(["", "## Frontend", ""])
    if frontend_notes:
        lines.extend(f"- {item}" for item in frontend_notes)
    else:
        lines.append(
            "- No se cuenta con evidencia suficiente para determinar una capa frontend concluyente."
        )

    lines.extend(["", "## Infraestructura", ""])
    if infrastructure_notes:
        lines.extend(f"- {item}" for item in infrastructure_notes)
    else:
        lines.append(
            "- No se identifica infraestructura declarativa relevante con la evidencia disponible."
        )

    lines.extend(["", "## Integraciones detectadas", ""])
    if integrations:
        lines.extend(f"- {item}" for item in integrations)
    else:
        lines.append("- No se identifican integraciones visibles en los artefactos relevados.")

    lines.extend(["", "## Observaciones", ""])
    lines.append(
        f"- El analisis automatico identifica las siguientes tecnologias globales: {technologies}."
    )

    lines.extend(["", "## Limitaciones del analisis", ""])
    lines.extend(f"- {item}" for item in limitations)
    return "\n".join(lines).strip() + "\n"
