"""Python technology detector."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from docucore.models import PluginResult
from docucore.plugins.base import BasePlugin

COMMON_BACKEND_DIRS = {
    "app",
    "api",
    "routes",
    "routers",
    "models",
    "schemas",
    "services",
    "core",
    "db",
    "database",
    "migrations",
}
HTTP_METHODS = ("get", "post", "put", "delete", "patch", "options", "head")


class PythonPlugin(BasePlugin):
    """Detect Python projects and simple FastAPI markers."""

    name = "python"

    def detect(self, project_root: Path, files: list[Path]) -> dict[str, object]:
        has_python = any(path.suffix == ".py" for path in files)
        has_pyproject = any(path.name == "pyproject.toml" for path in files)
        has_requirements = any(path.name == "requirements.txt" for path in files)
        return {
            "detected": has_python or has_pyproject or has_requirements,
            "has_pyproject": has_pyproject,
            "has_requirements": has_requirements,
        }

    def analyze(self, project_root: Path, files: list[Path]) -> PluginResult:
        python_files = [path for path in files if path.suffix == ".py"]
        pyproject_files = [path for path in files if path.name == "pyproject.toml"]
        requirement_files = [path for path in files if path.name == "requirements.txt"]
        python_directories = sorted(
            {path.parent.as_posix() for path in python_files if path.parent != Path(".")}
        )
        has_pyproject = bool(pyproject_files)
        has_requirements = bool(requirement_files)

        fastapi_detected = False
        marker_matches: set[str] = set()
        for relative_path in python_files[:100]:
            content = self.read_text(project_root / relative_path)
            if "fastapi" in content.lower():
                marker_matches.add("fastapi")
            if "APIRouter" in content:
                marker_matches.add("APIRouter")
            if "uvicorn" in content.lower():
                marker_matches.add("uvicorn")
        fastapi_detected = bool(marker_matches)
        dependencies = self._load_dependencies(project_root, pyproject_files, requirement_files)
        endpoints = self._detect_endpoints(project_root, python_files)
        backend_structure_dirs = sorted(
            {
                part
                for path in python_files
                for part in path.parts
                if part.lower() in COMMON_BACKEND_DIRS
            }
        )
        models = sorted(
            path.as_posix()
            for path in python_files
            if "models" in {part.lower() for part in path.parts}
        )
        schemas = sorted(
            path.as_posix()
            for path in python_files
            if "schemas" in {part.lower() for part in path.parts}
        )
        services = sorted(
            path.as_posix()
            for path in python_files
            if "services" in {part.lower() for part in path.parts}
        )

        technologies = ["python"] if (python_files or has_pyproject or has_requirements) else []
        if fastapi_detected:
            technologies.append("fastapi")

        findings = []
        if python_files:
            findings.append(f"Archivos Python detectados: {len(python_files)}.")
        if has_pyproject:
            findings.append("Se detecto pyproject.toml.")
        if has_requirements:
            findings.append("Se detecto requirements.txt.")
        if fastapi_detected:
            findings.append("Se detectaron indicadores simples de FastAPI.")
        if endpoints:
            findings.append(f"Endpoints detectados: {len(endpoints)}.")

        warnings = []
        if technologies and not (has_pyproject or has_requirements):
            warnings.append("Proyecto Python detectado sin pyproject.toml ni requirements.txt.")

        return PluginResult(
            name=self.name,
            detected=bool(technologies),
            technologies=technologies,
            findings=findings,
            warnings=warnings,
            data={
                "has_pyproject": has_pyproject,
                "has_requirements": has_requirements,
                "pyproject_files": [path.as_posix() for path in pyproject_files],
                "requirements_files": [path.as_posix() for path in requirement_files],
                "dependencies": dependencies,
                "python_directories": python_directories,
                "fastapi_detected": fastapi_detected,
                "fastapi_markers": sorted(marker_matches),
                "backend_structure_dirs": backend_structure_dirs,
                "endpoints": endpoints,
                "models": models,
                "schemas": schemas,
                "services": services,
            },
        )

    def _load_dependencies(
        self,
        project_root: Path,
        pyproject_files: list[Path],
        requirement_files: list[Path],
    ) -> list[str]:
        dependencies: set[str] = set()

        for requirement_file in requirement_files:
            for line in self.read_text(project_root / requirement_file).splitlines():
                cleaned = line.strip()
                if not cleaned or cleaned.startswith("#") or cleaned.startswith("-"):
                    continue
                dependency = re.split(r"[<>=!~\[]", cleaned, maxsplit=1)[0].strip()
                if dependency:
                    dependencies.add(dependency)

        for pyproject_file in pyproject_files:
            try:
                parsed = tomllib.loads(self.read_text(project_root / pyproject_file))
            except tomllib.TOMLDecodeError:
                continue
            project_section = parsed.get("project", {})
            for entry in project_section.get("dependencies", []):
                dependency = re.split(r"[<>=!~\[]", str(entry), maxsplit=1)[0].strip()
                if dependency:
                    dependencies.add(dependency)
            poetry_section = parsed.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for dependency in poetry_section:
                if dependency.lower() != "python":
                    dependencies.add(str(dependency))

        return sorted(dependencies)

    def _detect_endpoints(
        self,
        project_root: Path,
        python_files: list[Path],
    ) -> list[dict[str, str]]:
        decorator_pattern = re.compile(
            r"@\s*(?:\w+\.)?(?:router|app)\.(?P<method>get|post|put|delete|patch|options|head)"
            r"\(\s*[\"'](?P<path>[^\"']+)[\"']"
        )
        function_pattern = re.compile(
            r"^\s*(?:async\s+def|def)\s+(?P<handler>[A-Za-z_][A-Za-z0-9_]*)\s*\("
        )

        endpoints: list[dict[str, str]] = []
        for relative_path in python_files:
            lines = self.read_text(project_root / relative_path).splitlines()
            pending: list[dict[str, str]] = []
            for line in lines:
                decorator_match = decorator_pattern.search(line)
                if decorator_match:
                    pending.append(
                        {
                            "method": decorator_match.group("method").upper(),
                            "path": decorator_match.group("path"),
                            "file": relative_path.as_posix(),
                        }
                    )
                    continue
                function_match = function_pattern.match(line)
                if function_match and pending:
                    handler = function_match.group("handler")
                    for endpoint in pending:
                        endpoints.append({**endpoint, "handler": handler})
                    pending = []
            for endpoint in pending:
                endpoints.append({**endpoint, "handler": "unknown"})
        return endpoints
