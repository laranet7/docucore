"""Project scanning orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from docucore.core.config import RuntimeContext
from docucore.core.filesystem import iter_project_files
from docucore.models import ProjectConfig, ScanResult
from docucore.plugins import get_plugin


@dataclass(slots=True)
class ScanArtifacts:
    """Internal scan bundle used by generators and writers."""

    scan_result: ScanResult
    files: list[str]


def scan_project(context: RuntimeContext, config: ProjectConfig) -> ScanArtifacts:
    """Scan a repository using the enabled plugin list."""

    root = context.project_root.resolve()
    relative_files, directories = iter_project_files(
        root=root,
        include_paths=config.include_paths,
        exclude_paths=config.exclude_paths,
        documentation_root=context.documentation_root,
    )

    plugin_results = []
    warnings: list[str] = []
    for plugin_name in config.enabled_plugins:
        plugin = get_plugin(plugin_name)
        if plugin is None:
            warnings.append(f"Plugin no registrado: {plugin_name}.")
            continue
        detection = plugin.detect(root, relative_files)
        result = plugin.analyze(root, relative_files)
        result.detected = bool(detection.get("detected", result.detected))
        result.data.setdefault("detection", detection)
        plugin_results.append(result)

    technologies = sorted({tech for result in plugin_results for tech in result.technologies})
    findings = [finding for result in plugin_results for finding in result.findings]
    warnings.extend(warning for result in plugin_results for warning in result.warnings)

    scan_result = ScanResult(
        project_name=config.project_name,
        project_code=config.project_code,
        generated_at=datetime.now().astimezone().isoformat(),
        root_path=root.as_posix(),
        files_scanned=len(relative_files),
        directories_scanned=len(directories),
        plugins=plugin_results,
        technologies=technologies,
        findings=findings,
        warnings=warnings,
    )
    return ScanArtifacts(
        scan_result=scan_result,
        files=[path.as_posix() for path in relative_files],
    )
