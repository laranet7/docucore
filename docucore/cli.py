"""CLI entrypoint for DocuCore."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from docucore.core.config import (
    initialize_project,
    resolve_runtime_context,
)
from docucore.core.scanner import scan_project
from docucore.core.snapshot import create_snapshot_from_outputs
from docucore.core.status import collect_status
from docucore.core.writer import write_inventory_outputs

app = typer.Typer(help="DocuCore CLI for living documentation workflows.", no_args_is_help=True)
console = Console()

ForceOption = Annotated[
    bool,
    typer.Option("--force", help="Overwrite existing configuration."),
]
ProjectNameOption = Annotated[
    str,
    typer.Option("--project-name", help="Project display name."),
]
ProjectCodeOption = Annotated[
    str,
    typer.Option("--project-code", help="Short project code."),
]
ProjectOption = Annotated[
    Path | None,
    typer.Option("--project", help="Project root to analyze."),
]
OutputOption = Annotated[
    Path | None,
    typer.Option("--output", help="Documentation workspace output path."),
]
ConfigOption = Annotated[
    Path | None,
    typer.Option("--config", help="Explicit configuration file path."),
]

@app.command()
def init(
    force: ForceOption = False,
    project_name: ProjectNameOption = "Unnamed Project",
    project_code: ProjectCodeOption = "UNNAMED",
    project: ProjectOption = None,
    output: OutputOption = None,
    config: ConfigOption = None,
) -> None:
    """Initialize documentation structure for the current project."""

    try:
        context = resolve_runtime_context(
            project=project,
            output=output,
            config=config,
            require_config=False,
        )
        result = initialize_project(
            project_root=context.project_root,
            documentation_root=context.documentation_root,
            project_name=project_name,
            project_code=project_code,
            force=force,
        )
    except Exception as exc:
        console.print(f"[red]Initialization failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    created_directories = [
        path.relative_to(context.documentation_root).as_posix()
        for path in result["created_directories"]
    ]
    console.print("[green]DocuCore initialized.[/green]")
    console.print(f"Project root: {context.project_root}")
    console.print(f"Documentation path: {context.documentation_root}")
    console.print(f"Configuration: {Path(result['config_path'])}")
    if created_directories:
        console.print(f"Directories created: {len(created_directories)}")
    if result["config_overwritten"]:
        console.print("Existing configuration overwritten with --force.")
    elif result["config_created"]:
        console.print("Configuration file created.")
    else:
        console.print("Existing configuration preserved.")


@app.command()
def scan(
    project: ProjectOption = None,
    output: OutputOption = None,
    config: ConfigOption = None,
) -> None:
    """Scan the project and generate inventory outputs."""

    try:
        context = resolve_runtime_context(
            project=project,
            output=output,
            config=config,
            require_config=True,
        )
        if context.config is None:
            raise FileNotFoundError(f"Configuration file not found: {context.config_path}")
        scan_artifacts = scan_project(context, context.config)
        inventory, output_paths = write_inventory_outputs(context, context.config, scan_artifacts)
    except Exception as exc:
        console.print(f"[red]Scan failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[green]Scan completed.[/green]")
    console.print(f"Project root: {context.project_root}")
    console.print(f"Documentation path: {context.documentation_root}")
    console.print(f"Files scanned: {scan_artifacts.scan_result.files_scanned}")
    technologies = ", ".join(inventory.technologies) if inventory.technologies else "none"
    console.print(f"Technologies detected: {technologies}")
    rendered_outputs = (
        ", ".join(str(path) for path in output_paths.values()) if output_paths else "none"
    )
    console.print(f"Outputs: {rendered_outputs}")


@app.command()
def build(
    project: ProjectOption = None,
    output: OutputOption = None,
    config: ConfigOption = None,
) -> None:
    """Run scan, snapshot, latest update and manifest generation."""

    try:
        context = resolve_runtime_context(
            project=project,
            output=output,
            config=config,
            require_config=True,
        )
        if context.config is None:
            raise FileNotFoundError(f"Configuration file not found: {context.config_path}")
        scan_artifacts = scan_project(context, context.config)
        inventory, _ = write_inventory_outputs(context, context.config, scan_artifacts)
        snapshot_artifacts = create_snapshot_from_outputs(context, context.config)
    except Exception as exc:
        console.print(f"[red]Build failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[green]Build completed.[/green]")
    console.print(f"Project root: {context.project_root}")
    console.print(f"Documentation path: {context.documentation_root}")
    console.print(f"Snapshot: {snapshot_artifacts.snapshot_id}")
    console.print(f"Latest outputs ready at {snapshot_artifacts.latest_dir}")
    if inventory.warnings:
        console.print(f"Warnings: {len(inventory.warnings)}")


@app.command()
def snapshot(
    project: ProjectOption = None,
    output: OutputOption = None,
    config: ConfigOption = None,
) -> None:
    """Create a historical snapshot from existing outputs."""

    try:
        context = resolve_runtime_context(
            project=project,
            output=output,
            config=config,
            require_config=True,
        )
        if context.config is None:
            raise FileNotFoundError(f"Configuration file not found: {context.config_path}")
        snapshot_artifacts = create_snapshot_from_outputs(context, context.config)
    except Exception as exc:
        console.print(f"[red]Snapshot failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[green]Snapshot created.[/green]")
    console.print(f"Project root: {context.project_root}")
    console.print(f"Documentation path: {context.documentation_root}")
    console.print(f"Snapshot ID: {snapshot_artifacts.snapshot_id}")
    console.print(f"Historical path: {snapshot_artifacts.historical_dir}")


@app.command()
def status(
    project: ProjectOption = None,
    output: OutputOption = None,
    config: ConfigOption = None,
) -> None:
    """Show the documentation status for the current project."""

    try:
        context = resolve_runtime_context(
            project=project,
            output=output,
            config=config,
            require_config=False,
        )
        status_data = collect_status(context)
    except Exception as exc:
        console.print(f"[red]Status failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[bold]DocuCore status[/bold]")
    console.print(f"Project root: {status_data['project_root']}")
    console.print(f"Documentation path: {status_data['documentation_path']}")
    console.print(f"Config present: {'yes' if status_data['config_exists'] else 'no'}")
    console.print(f"Latest present: {'yes' if status_data['latest_exists'] else 'no'}")
    console.print(f"Last snapshot: {status_data['last_snapshot'] or 'none'}")
    console.print(
        "Outputs available: "
        f"{', '.join(status_data['latest_outputs']) if status_data['latest_outputs'] else 'none'}"
    )
    console.print(
        "Enabled plugins: "
        f"{', '.join(status_data['enabled_plugins']) if status_data['enabled_plugins'] else 'none'}"
    )


if __name__ == "__main__":
    app()
