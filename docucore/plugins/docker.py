"""Docker technology detector."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from docucore.models import PluginResult
from docucore.plugins.base import BasePlugin

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised indirectly in environments without PyYAML
    yaml = None


class DockerPlugin(BasePlugin):
    """Detect Dockerfiles and Compose descriptors."""

    name = "docker"

    def detect(self, project_root: Path, files: list[Path]) -> dict[str, object]:
        has_dockerfile = any(path.name == "Dockerfile" for path in files)
        has_compose = any(
            path.name in {"docker-compose.yml", "docker-compose.yaml"} for path in files
        )
        return {
            "detected": has_dockerfile or has_compose,
            "has_dockerfile": has_dockerfile,
            "has_compose": has_compose,
        }

    def analyze(self, project_root: Path, files: list[Path]) -> PluginResult:
        dockerfiles = [path.as_posix() for path in files if path.name == "Dockerfile"]
        compose_path = next(
            (path for path in files if path.name in {"docker-compose.yml", "docker-compose.yaml"}),
            None,
        )
        services: list[str] = []
        ports: list[str] = []
        services_details: list[dict[str, Any]] = []
        warnings: list[str] = []

        if compose_path is not None:
            content = self.read_text(project_root / compose_path)
            if yaml is None:
                services_details = self._fallback_parse_compose(content)
                services = [service["name"] for service in services_details]
                for service in services_details:
                    ports.extend(service["ports"])
                warnings.append("PyYAML no esta disponible; se uso parsing textual basico.")
            else:
                try:
                    parsed = yaml.safe_load(content) or {}
                    if not isinstance(parsed, dict):
                        raise ValueError("Compose root is not a mapping.")
                    compose_services = parsed.get("services", {})
                    if not isinstance(compose_services, dict):
                        raise ValueError("Compose services section is not a mapping.")
                    services_details = self._parse_compose_services(compose_services)
                    services = [service["name"] for service in services_details]
                    for service in services_details:
                        ports.extend(service["ports"])
                except Exception:
                    services_details = self._fallback_parse_compose(content)
                    services = [service["name"] for service in services_details]
                    for service in services_details:
                        ports.extend(service["ports"])
                    warnings.append(
                        "No se pudo parsear docker-compose.yml con PyYAML; "
                        "se uso parsing textual basico."
                    )

        technologies = []
        if dockerfiles or compose_path is not None:
            technologies.append("docker")
        if compose_path is not None:
            technologies.append("docker-compose")

        findings = []
        if dockerfiles:
            findings.append(f"Dockerfiles detectados: {len(dockerfiles)}.")
        if compose_path is not None:
            findings.append("Se detecto archivo docker-compose.")
        if services:
            findings.append(f"Servicios Compose detectados: {', '.join(services)}.")

        return PluginResult(
            name=self.name,
            detected=bool(technologies),
            technologies=technologies,
            findings=findings,
            warnings=warnings,
            data={
                "dockerfiles": dockerfiles,
                "compose_file": compose_path.as_posix() if compose_path else None,
                "services": services,
                "services_details": services_details,
                "ports": sorted(set(ports)),
            },
        )

    def _parse_compose_services(self, compose_services: dict[str, Any]) -> list[dict[str, Any]]:
        services: list[dict[str, Any]] = []
        for name, service_data in compose_services.items():
            build_data = service_data.get("build")
            build_context = ""
            dockerfile = ""
            if isinstance(build_data, str):
                build_context = build_data
            elif isinstance(build_data, dict):
                build_context = str(build_data.get("context", ""))
                dockerfile = str(build_data.get("dockerfile", ""))

            environment = service_data.get("environment", {})
            if isinstance(environment, dict):
                environment_vars = sorted(str(key) for key in environment)
            elif isinstance(environment, list):
                environment_vars = sorted(
                    str(item).split("=", maxsplit=1)[0] for item in environment
                )
            else:
                environment_vars = []

            depends_on = service_data.get("depends_on", [])
            if isinstance(depends_on, dict):
                depends_on_values = sorted(str(key) for key in depends_on)
            else:
                depends_on_values = sorted(str(item) for item in depends_on)

            networks = service_data.get("networks", [])
            if isinstance(networks, dict):
                network_values = sorted(str(key) for key in networks)
            else:
                network_values = sorted(str(item) for item in networks)

            ports = [str(port) for port in service_data.get("ports", [])]
            volumes = [str(volume) for volume in service_data.get("volumes", [])]
            services.append(
                {
                    "name": name,
                    "image": str(service_data.get("image", "")),
                    "build_context": build_context,
                    "dockerfile": dockerfile,
                    "ports": ports,
                    "volumes": volumes,
                    "environment": environment_vars,
                    "depends_on": depends_on_values,
                    "networks": network_values,
                }
            )
        return services

    def _fallback_parse_compose(self, content: str) -> list[dict[str, Any]]:
        services: list[dict[str, Any]] = []
        in_services = False
        service_regex = re.compile(r"^\s{2}([A-Za-z0-9_.-]+):\s*$")
        port_regex = re.compile(r"^\s*-\s*['\"]?([^'\"]+)['\"]?\s*$")
        pending_service: dict[str, Any] | None = None

        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "services:":
                in_services = True
                continue
            if in_services and not line.startswith("  "):
                in_services = False
            if in_services:
                service_match = service_regex.match(line)
                if service_match:
                    if pending_service is not None:
                        services.append(pending_service)
                    pending_service = {
                        "name": service_match.group(1),
                        "image": "",
                        "build_context": "",
                        "dockerfile": "",
                        "ports": [],
                        "volumes": [],
                        "environment": [],
                        "depends_on": [],
                        "networks": [],
                    }
                elif "ports:" in stripped:
                    continue
                else:
                    port_match = port_regex.match(line)
                    if (
                        pending_service is not None
                        and port_match
                        and ":" in port_match.group(1)
                    ):
                        pending_service["ports"].append(port_match.group(1))
        if pending_service is not None:
            services.append(pending_service)

        unique_services = []
        seen = set()
        for service in services:
            if service["name"] in seen:
                continue
            seen.add(service["name"])
            service["ports"] = sorted(set(service["ports"]))
            unique_services.append(service)
        return unique_services
