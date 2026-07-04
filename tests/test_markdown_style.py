from pathlib import Path

from docucore.core.config import initialize_project, resolve_runtime_context
from docucore.core.scanner import scan_project
from docucore.core.writer import write_inventory_outputs

FORBIDDEN_PHRASES = [
    "se presenta en este workspace como",
    "observamos que",
    "podemos ver que",
    "en este analisis vemos",
    "este informe considera que",
    "desde esta revision",
]


def test_generated_markdown_uses_institutional_objective_style(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    (project_root / "backend").mkdir(parents=True)
    (project_root / "backend" / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = resolve_runtime_context(
        project=project_root,
        output=documentation_root,
        require_config=True,
    )
    assert context.config is not None

    scan_artifacts = scan_project(context, context.config)
    _, written_outputs = write_inventory_outputs(context, context.config, scan_artifacts)

    markdown_contents = []
    for output_name, output_path in written_outputs.items():
        if not output_name.endswith(".md"):
            continue
        markdown_contents.append(output_path.read_text(encoding="utf-8").lower())

    combined = "\n".join(markdown_contents)
    for forbidden_phrase in FORBIDDEN_PHRASES:
        assert forbidden_phrase not in combined
