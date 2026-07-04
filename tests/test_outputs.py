from __future__ import annotations

import json
from pathlib import Path

from docucore.core.config import initialize_project, resolve_runtime_context
from docucore.core.scanner import scan_project
from docucore.core.snapshot import create_snapshot_from_outputs
from docucore.core.writer import write_inventory_outputs


def build_context(project_root: Path, documentation_root: Path):
    return resolve_runtime_context(
        project=project_root,
        output=documentation_root,
        require_config=True,
    )


def test_git_directory_is_excluded_from_visible_structure(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    (project_root / ".git").mkdir(parents=True)
    (project_root / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (project_root / "backend").mkdir(parents=True)
    (project_root / "backend" / "main.py").write_text("print('ok')\n", encoding="utf-8")

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = build_context(project_root, documentation_root)
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    generic_plugin = next(
        plugin for plugin in artifacts.scan_result.plugins if plugin.name == "generic"
    )

    assert ".git/config" not in artifacts.files
    assert ".git" not in generic_plugin.data["main_directories"]


def test_docker_compose_detection_with_pyyaml(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    project_root.mkdir(parents=True)
    (project_root / "docker-compose.yml").write_text(
        """
services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      APP_ENV: dev
  db:
    image: postgres:16
    ports:
      - "5432:5432"
""".strip(),
        encoding="utf-8",
    )

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = build_context(project_root, documentation_root)
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    docker_plugin = next(
        plugin for plugin in artifacts.scan_result.plugins if plugin.name == "docker"
    )
    services = docker_plugin.data["services_details"]
    api_service = next(service for service in services if service["name"] == "api")

    assert docker_plugin.warnings == []
    assert api_service["ports"] == ["8000:8000"]
    assert api_service["depends_on"] == ["db"]
    assert api_service["environment"] == ["APP_ENV"]


def test_backend_fastapi_detection_finds_endpoint(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    (project_root / "backend" / "api").mkdir(parents=True)
    (project_root / "backend" / "api" / "routes.py").write_text(
        """
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def healthcheck():
    return {"ok": True}
""".strip(),
        encoding="utf-8",
    )
    (project_root / "requirements.txt").write_text("fastapi\nuvicorn\n", encoding="utf-8")

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = build_context(project_root, documentation_root)
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    python_plugin = next(
        plugin for plugin in artifacts.scan_result.plugins if plugin.name == "python"
    )
    endpoint = python_plugin.data["endpoints"][0]

    assert python_plugin.data["fastapi_detected"] is True
    assert endpoint["method"] == "GET"
    assert endpoint["path"] == "/health"
    assert endpoint["handler"] == "healthcheck"


def test_frontend_vue_vite_detection_finds_component_and_route(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    (project_root / "frontend" / "src" / "components").mkdir(parents=True)
    (project_root / "frontend" / "src" / "views").mkdir(parents=True)
    (project_root / "frontend" / "src" / "router").mkdir(parents=True)
    (project_root / "frontend" / "package.json").write_text(
        json.dumps(
            {
                "scripts": {"dev": "vite", "build": "vite build"},
                "dependencies": {"vue": "^3.0.0", "vue-router": "^4.0.0"},
                "devDependencies": {"vite": "^5.0.0"},
            }
        ),
        encoding="utf-8",
    )
    (project_root / "frontend" / "src" / "components" / "HelloWorld.vue").write_text(
        "<template><div>Hello</div></template>",
        encoding="utf-8",
    )
    (project_root / "frontend" / "src" / "views" / "HomeView.vue").write_text(
        "<template><div>Home</div></template>",
        encoding="utf-8",
    )
    (project_root / "frontend" / "src" / "router" / "index.ts").write_text(
        """
import { createRouter } from "vue-router"

const routes = [
  { path: "/", name: "home", component: {} },
]

export default createRouter({ routes })
""".strip(),
        encoding="utf-8",
    )

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = build_context(project_root, documentation_root)
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    node_plugin = next(plugin for plugin in artifacts.scan_result.plugins if plugin.name == "node")

    assert "vue" in node_plugin.data["frameworks"]
    assert "vite" in node_plugin.data["frameworks"]
    assert "dev" in node_plugin.data["scripts"]
    assert any(path.endswith("HelloWorld.vue") for path in node_plugin.data["components"])
    assert any(route["path"] == "/" for route in node_plugin.data["routes"])


def test_build_generates_new_documents_and_manifest_entries(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    (project_root / "backend").mkdir(parents=True)
    (project_root / "backend" / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )
    (project_root / "frontend" / "src" / "components").mkdir(parents=True)
    (project_root / "frontend" / "package.json").write_text(
        json.dumps(
            {
                "scripts": {"dev": "vite"},
                "dependencies": {"vue": "^3.0.0"},
                "devDependencies": {"vite": "^5.0.0"},
            }
        ),
        encoding="utf-8",
    )
    (project_root / "docker-compose.yml").write_text(
        "services:\n  api:\n    image: demo\n",
        encoding="utf-8",
    )

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    context = build_context(project_root, documentation_root)
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    _, outputs = write_inventory_outputs(context, context.config, artifacts)
    snapshot = create_snapshot_from_outputs(context, context.config)
    manifest_path = documentation_root / "latest" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "architecture.md" in outputs
    assert (documentation_root / "outputs" / "architecture" / "architecture.md").exists()
    assert (documentation_root / "latest" / "frontend.md").exists()
    assert (snapshot.historical_dir / "backend.md").exists()
    assert "modules.md" in manifest["outputs"]
    assert "infrastructure.md" in manifest["outputs"]


def test_backward_compatibility_with_old_output_configuration(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    documentation_root = tmp_path / "docs"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")

    initialize_project(project_root, documentation_root, project_name="Demo", project_code="DEMO")
    config_path = documentation_root / "config" / "project.config.json"
    raw_config = json.loads(config_path.read_text(encoding="utf-8"))
    raw_config["outputs"] = ["inventory", "snapshot"]
    config_path.write_text(json.dumps(raw_config, indent=2), encoding="utf-8")

    context = build_context(project_root, documentation_root)
    assert context.config is not None

    artifacts = scan_project(context, context.config)
    write_inventory_outputs(context, context.config, artifacts)
    create_snapshot_from_outputs(context, context.config)

    assert (documentation_root / "latest" / "inventory.md").exists()
    assert not (documentation_root / "latest" / "architecture.md").exists()
    assert not (documentation_root / "outputs" / "backend" / "backend.md").exists()
