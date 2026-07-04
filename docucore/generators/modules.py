"""Modules Markdown generator."""

from __future__ import annotations

from docucore.core.scanner import ScanArtifacts
from docucore.generators.common import first_level_directories, get_plugin_data
from docucore.models import Inventory


def build_modules_markdown(scan_artifacts: ScanArtifacts, inventory: Inventory) -> str:
    """Generate the modules Markdown document."""

    python_data = get_plugin_data(scan_artifacts, "python")
    node_data = get_plugin_data(scan_artifacts, "node")
    docker_data = get_plugin_data(scan_artifacts, "docker")

    backend_modules = first_level_directories(scan_artifacts.files, "backend")
    if not backend_modules:
        backend_modules = list(python_data.get("backend_structure_dirs", []))

    frontend_root = node_data.get("frontend_root", "")
    frontend_modules = []
    if isinstance(frontend_root, str) and frontend_root:
        frontend_modules = first_level_directories(scan_artifacts.files, f"{frontend_root}/src")

    infrastructure_modules = list(docker_data.get("services", []))
    inferred_functional = sorted(
        {
            *backend_modules,
            *frontend_modules,
            *[segment for segment in _endpoint_segments(python_data.get("endpoints", []))],
        }
    )

    technologies = ", ".join(inventory.technologies) if inventory.technologies else "sin datos"

    lines = [
        "# Modulos detectados",
        "",
        "## Proyecto",
        "",
        f"- Nombre: {scan_artifacts.scan_result.project_name}",
        f"- Codigo: {scan_artifacts.scan_result.project_code}",
        "",
        "## Resumen",
        "",
        "- La deteccion de modulos se basa en estructura de carpetas, archivos y rutas visibles.",
        f"- Tecnologias detectadas: {technologies}",
        f"- Archivos analizados: {scan_artifacts.scan_result.files_scanned}",
        "",
        "## Modulos backend",
        "",
    ]
    if backend_modules:
        lines.extend(f"- {item}" for item in backend_modules)
    else:
        lines.append("- No se identifican modulos backend con evidencia suficiente.")

    lines.extend(["", "## Modulos frontend", ""])
    if frontend_modules:
        lines.extend(f"- {item}" for item in frontend_modules)
    else:
        lines.append("- No se identifican modulos frontend con evidencia suficiente.")

    lines.extend(["", "## Modulos de infraestructura", ""])
    if infrastructure_modules:
        lines.extend(f"- {item}" for item in infrastructure_modules)
    else:
        lines.append("- No se identifican modulos de infraestructura con evidencia suficiente.")

    lines.extend(["", "## Posibles modulos funcionales", ""])
    if inferred_functional:
        lines.extend(
            f"- {item} (inferencia basada en nombres de carpetas, archivos o rutas detectadas)"
            for item in inferred_functional
        )
    else:
        lines.append("- No se cuenta con evidencia suficiente para inferir modulos funcionales.")

    lines.extend(["", "## Limitaciones", ""])
    lines.append(
        "- Los modulos funcionales son inferidos y pueden no coincidir con limites de "
        "dominio reales."
    )
    lines.append(
        "- Esta conclusion debe validarse con revision tecnica manual cuando se requiera "
        "confirmar limites funcionales."
    )
    return "\n".join(lines).strip() + "\n"


def _endpoint_segments(endpoints: object) -> set[str]:
    segments: set[str] = set()
    if not isinstance(endpoints, list):
        return segments
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        path = str(endpoint.get("path", "")).strip("/")
        if not path:
            continue
        first_segment = path.split("/", maxsplit=1)[0]
        if first_segment and "{" not in first_segment:
            segments.add(first_segment)
    return segments
