from pathlib import Path

from docucore.core.config import initialize_project, resolve_runtime_context
from docucore.core.scanner import scan_project


def test_scanner_respects_exclusions_and_writes_outside_project(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "workspace" / "docs"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "app.py").write_text("from fastapi import FastAPI\n", encoding="utf-8")
    (project_root / "node_modules").mkdir()
    (project_root / "node_modules" / "index.js").write_text(
        "console.log('ignore')",
        encoding="utf-8",
    )
    (project_root / "README.md").write_text("# Demo\n", encoding="utf-8")

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = resolve_runtime_context(
        project=project_root,
        output=documentation_root,
        require_config=True,
    )
    assert context.config is not None

    artifacts = scan_project(context, context.config)

    assert "node_modules/index.js" not in artifacts.files
    assert "src/app.py" in artifacts.files
    assert "python" in artifacts.scan_result.technologies
    assert not (project_root / "documentacion").exists()


def test_scanner_ignores_documentation_when_output_is_inside_project(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = project_root / "documentacion"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = resolve_runtime_context(project=project_root, require_config=True)
    assert context.config is not None

    artifacts = scan_project(context, context.config)

    assert all(not file_path.startswith("documentacion/") for file_path in artifacts.files)
