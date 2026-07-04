"""Node.js technology detector."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from docucore.models import PluginResult
from docucore.plugins.base import BasePlugin

FRAMEWORK_MARKERS = {
    "vue": ("vue",),
    "nuxt": ("nuxt",),
    "react": ("react",),
    "next": ("next",),
    "express": ("express",),
    "vite": ("vite",),
}


class NodePlugin(BasePlugin):
    """Detect Node-based repositories from package.json and JS/TS files."""

    name = "node"

    def detect(self, project_root: Path, files: list[Path]) -> dict[str, object]:
        has_package_json = any(path.name == "package.json" for path in files)
        has_js_ts = any(path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx"} for path in files)
        return {"detected": has_package_json or has_js_ts, "has_package_json": has_package_json}

    def analyze(self, project_root: Path, files: list[Path]) -> PluginResult:
        package_paths = [path for path in files if path.name == "package.json"]
        scripts: dict[str, str] = {}
        dependency_names: set[str] = set()
        warnings: list[str] = []
        package_summaries = self._load_package_summaries(project_root, package_paths, warnings)
        selected_package = self._select_frontend_package(package_summaries)
        frameworks = sorted(
            {
                framework
                for package in package_summaries
                for framework in package.get("frameworks", [])
            }
        )

        frontend_root = ""
        frontend_structure: list[str] = []
        components: list[str] = []
        views_pages: list[str] = []
        routes: list[dict[str, str]] = []
        stores: list[str] = []
        composables: list[str] = []
        config_files: list[str] = []

        if selected_package is not None:
            scripts = dict(selected_package.get("scripts", {}))
            dependency_names = set(selected_package.get("dependencies", []))
            frontend_root = str(selected_package.get("root", ""))
            frontend_structure = self._detect_frontend_structure(project_root, frontend_root)
            components = self._list_files_under(
                project_root,
                frontend_root,
                ("src/components",),
                (".vue",),
            )
            views_pages = self._list_files_under(
                project_root,
                frontend_root,
                ("src/views", "src/pages"),
                (".vue", ".js", ".ts", ".tsx", ".jsx"),
            )
            stores = self._list_files_under(
                project_root,
                frontend_root,
                ("src/stores", "src/store"),
                (".js", ".ts", ".tsx", ".jsx"),
            )
            composables = self._list_files_under(
                project_root,
                frontend_root,
                ("src/composables",),
                (".js", ".ts", ".tsx", ".jsx"),
            )
            router_files = self._list_files_under(
                project_root,
                frontend_root,
                ("src/router", "src/routes"),
                (".js", ".ts", ".tsx", ".jsx"),
            )
            routes = self._detect_routes(project_root, router_files)
            config_files = self._detect_config_files(project_root, frontend_root)

        technologies = []
        if package_paths or any(
            path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx"} for path in files
        ):
            technologies.append("node")
        technologies.extend(frameworks)

        findings = []
        if package_paths:
            findings.append(f"Archivos package.json detectados: {len(package_paths)}.")
        if scripts:
            findings.append(f"Scripts de npm detectados: {len(scripts)}.")
        if frameworks:
            findings.append(f"Frameworks detectados: {', '.join(frameworks)}.")
        if components:
            findings.append(f"Componentes frontend detectados: {len(components)}.")
        if routes:
            findings.append(f"Rutas frontend detectadas: {len(routes)}.")

        return PluginResult(
            name=self.name,
            detected=bool(technologies),
            technologies=technologies,
            findings=findings,
            warnings=warnings,
            data={
                "package_files": [path.as_posix() for path in package_paths],
                "package_json": selected_package["path"] if selected_package else None,
                "dependencies": sorted(dependency_names),
                "scripts": scripts,
                "frameworks": frameworks,
                "frontend_root": frontend_root,
                "frontend_structure": frontend_structure,
                "components": components,
                "views_pages": views_pages,
                "routes": routes,
                "stores": stores,
                "composables": composables,
                "config_files": config_files,
            },
        )

    def _load_package_summaries(
        self,
        project_root: Path,
        package_paths: list[Path],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        packages: list[dict[str, Any]] = []
        for package_path in package_paths:
            try:
                package_data = json.loads(self.read_text(project_root / package_path))
            except json.JSONDecodeError:
                warnings.append(f"No fue posible parsear package.json: {package_path.as_posix()}.")
                continue
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            dependency_names = sorted(set(dependencies) | set(dev_dependencies))
            frameworks = [
                framework
                for framework, markers in FRAMEWORK_MARKERS.items()
                if any(marker in dependency_names for marker in markers)
            ]
            root = package_path.parent.as_posix()
            score = len(frameworks) * 2
            if (project_root / package_path.parent / "src").exists():
                score += 2
            if package_path.parent.name.lower() in {"frontend", "web", "client", "ui"}:
                score += 1
            packages.append(
                {
                    "path": package_path.as_posix(),
                    "root": root if root != "." else "",
                    "dependencies": dependency_names,
                    "frameworks": frameworks,
                    "scripts": package_data.get("scripts", {}),
                    "score": score,
                }
            )
        return packages

    def _select_frontend_package(self, packages: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not packages:
            return None
        return sorted(
            packages,
            key=lambda package: (
                package["score"],
                1 if str(package["root"]).startswith("frontend") else 0,
                len(str(package["root"])),
            ),
            reverse=True,
        )[0]

    def _detect_frontend_structure(self, project_root: Path, frontend_root: str) -> list[str]:
        if not frontend_root:
            base = project_root
        else:
            base = project_root / frontend_root
        structure = []
        for candidate in [
            "src",
            "src/components",
            "src/views",
            "src/pages",
            "src/router",
            "src/routes",
            "src/stores",
            "src/composables",
        ]:
            if (base / candidate).exists():
                structure.append(candidate)
        return structure

    def _list_files_under(
        self,
        project_root: Path,
        frontend_root: str,
        prefixes: tuple[str, ...],
        suffixes: tuple[str, ...],
    ) -> list[str]:
        base = project_root / frontend_root if frontend_root else project_root
        matches: list[str] = []
        for prefix in prefixes:
            candidate = base / prefix
            if not candidate.exists():
                continue
            for file_path in candidate.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in suffixes:
                    matches.append(file_path.relative_to(project_root).as_posix())
        return sorted(set(matches))

    def _detect_routes(self, project_root: Path, router_files: list[str]) -> list[dict[str, str]]:
        path_pattern = re.compile(r"path\s*:\s*[\"'](?P<path>[^\"']+)[\"']")
        name_pattern = re.compile(r"name\s*:\s*[\"'](?P<name>[^\"']+)[\"']")
        routes: list[dict[str, str]] = []
        for router_file in router_files:
            lines = self.read_text(project_root / router_file).splitlines()
            for index, line in enumerate(lines):
                path_match = path_pattern.search(line)
                if not path_match:
                    continue
                route_name = ""
                for lookahead in lines[index : index + 6]:
                    name_match = name_pattern.search(lookahead)
                    if name_match:
                        route_name = name_match.group("name")
                        break
                routes.append(
                    {
                        "path": path_match.group("path"),
                        "name": route_name,
                        "file": router_file,
                    }
                )
        return routes

    def _detect_config_files(self, project_root: Path, frontend_root: str) -> list[str]:
        base = project_root / frontend_root if frontend_root else project_root
        matches = []
        for pattern in ("vite.config.*", "nuxt.config.*"):
            matches.extend(path.relative_to(project_root).as_posix() for path in base.glob(pattern))
        return sorted(set(matches))
