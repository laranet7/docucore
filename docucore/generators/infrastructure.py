"""Infrastructure Markdown generator."""

from __future__ import annotations

from docucore.core.scanner import ScanArtifacts
from docucore.generators.common import get_plugin_data
from docucore.models import Inventory


def build_infrastructure_markdown(scan_artifacts: ScanArtifacts, inventory: Inventory) -> str:
    """Generate the infrastructure Markdown document."""

    generic_data = get_plugin_data(scan_artifacts, "generic")
    docker_data = get_plugin_data(scan_artifacts, "docker")

    dockerfiles = list(docker_data.get("dockerfiles", []))
    services = list(docker_data.get("services_details", []))
    compose_file = docker_data.get("compose_file")
    github_workflows = list(generic_data.get("github_workflow_files", []))
    gitlab_ci = list(generic_data.get("gitlab_ci_files", []))
    environment_vars = sorted(
        {
            variable
            for service in services
            for variable in service.get("environment", [])
        }
    )

    lines = [
        "# Infraestructura detectada",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {scan_artifacts.scan_result.project_name}",
        f"- Codigo: {scan_artifacts.scan_result.project_code}",
        "",
        "## Resumen",
        "",
    ]
    if dockerfiles or compose_file or github_workflows or gitlab_ci:
        lines.append(
            f"- El relevamiento detecta {len(dockerfiles)} Dockerfiles y {len(services)} "
            f"servicios Compose."
        )
        if github_workflows:
            lines.append("- Se identifican workflows de GitHub Actions.")
        if gitlab_ci:
            lines.append("- Se identifica configuracion de GitLab CI.")
    else:
        lines.append(
            "- No se identifica infraestructura declarativa relevante con la evidencia disponible."
        )

    lines.extend(["", "## Docker", ""])
    if dockerfiles:
        lines.extend(f"- {item}" for item in dockerfiles)
    else:
        lines.append("- No se identifican Dockerfiles.")

    lines.extend(["", "## Docker Compose", ""])
    if compose_file:
        lines.append(f"- Archivo detectado: {compose_file}")
    else:
        lines.append("- No se identifica archivo docker-compose.")

    lines.extend(["", "## Servicios", ""])
    if services:
        lines.extend(
            [
                "",
                "| Servicio | Imagen/Build | Puertos | Depends on |",
                "| -------- | ------------ | ------- | ---------- |",
            ]
        )
        for service in services:
            image_or_build = service.get("image") or service.get("build_context") or ""
            if service.get("dockerfile"):
                image_or_build = f"{image_or_build} ({service.get('dockerfile')})".strip()
            ports = ", ".join(service.get("ports", []))
            depends_on = ", ".join(service.get("depends_on", []))
            lines.append(
                f"| {service.get('name', '')} | {image_or_build} | {ports} | {depends_on} |"
            )
    else:
        lines.append("- No se identifican servicios Compose.")

    lines.extend(["", "## CI/CD detectado", ""])
    if github_workflows:
        lines.append(f"- GitHub Actions: {', '.join(github_workflows)}")
    if gitlab_ci:
        lines.append(f"- GitLab CI: {', '.join(gitlab_ci)}")
    if not any([github_workflows, gitlab_ci]):
        lines.append("- No se identifica CI/CD visible.")

    lines.extend(["", "## Variables y configuracion", ""])
    if environment_vars:
        lines.append(f"- Variables de entorno declaradas: {', '.join(environment_vars)}")
    else:
        lines.append("- No se identifican variables de entorno declaradas en Compose.")

    lines.extend(["", "## Limitaciones", ""])
    lines.append(
        "- El analisis de infraestructura depende de archivos declarativos visibles en el "
        "repositorio."
    )
    lines.append(
        "- No se cuenta con evidencia suficiente para determinar configuraciones externas o "
        "generadas dinamicamente."
    )
    return "\n".join(lines).strip() + "\n"
