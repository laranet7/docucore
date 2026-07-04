"""Dotnet technology detector."""

from __future__ import annotations

from pathlib import Path

from docucore.models import PluginResult
from docucore.plugins.base import BasePlugin


class DotnetPlugin(BasePlugin):
    """Detect .NET solutions and simple ASP.NET markers."""

    name = "dotnet"

    def detect(self, project_root: Path, files: list[Path]) -> dict[str, object]:
        has_solution = any(path.suffix == ".sln" for path in files)
        has_csproj = any(path.suffix == ".csproj" for path in files)
        return {"detected": has_solution or has_csproj, "has_solution": has_solution}

    def analyze(self, project_root: Path, files: list[Path]) -> PluginResult:
        solutions = [path.as_posix() for path in files if path.suffix == ".sln"]
        projects = [path.as_posix() for path in files if path.suffix == ".csproj"]
        program_cs = any(path.name == "Program.cs" for path in files)
        startup_cs = any(path.name == "Startup.cs" for path in files)
        controllers = [path.as_posix() for path in files if "Controllers" in path.parts]

        aspnet = False
        for relative_path in [Path(project) for project in projects]:
            content = self.read_text(project_root / relative_path)
            if "Microsoft.AspNetCore" in content:
                aspnet = True
                break
        aspnet = aspnet or program_cs or startup_cs or bool(controllers)

        technologies = []
        if solutions or projects:
            technologies.append("dotnet")
        if aspnet:
            technologies.append("aspnet")

        findings = []
        if solutions:
            findings.append(f"Soluciones detectadas: {len(solutions)}.")
        if projects:
            findings.append(f"Proyectos .csproj detectados: {len(projects)}.")
        if aspnet:
            findings.append("Se detectaron indicadores simples de ASP.NET.")

        return PluginResult(
            name=self.name,
            detected=bool(technologies),
            technologies=technologies,
            findings=findings,
            data={
                "solutions": solutions,
                "projects": projects,
                "program_cs": program_cs,
                "startup_cs": startup_cs,
                "controllers": controllers,
                "aspnet_detected": aspnet,
            },
        )

