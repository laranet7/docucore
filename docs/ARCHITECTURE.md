# Architecture

## Overview

DocuCore is organized as a reusable documentation engine with clear separation between scanning, structured analysis, document generation, export, and orchestration.

## Core

`docucore/core` contains the execution services that coordinate configuration loading, runtime resolution, filesystem traversal, output planning, snapshots, status reporting, and manifest generation.

## CLI

`docucore/cli.py` exposes the public commands:

- `init`
- `scan`
- `build`
- `snapshot`
- `status`

The CLI is intentionally thin and delegates behavior to the core services.

## Runtime context

The runtime context resolves:

- the project being read
- the documentation destination being written
- the configuration file to load

This design allows DocuCore to work both on the current project and on external repositories through `--project` and `--output`.

## Scanner

The scanner walks the repository according to `include_paths` and `exclude_paths`, collects filtered files, and passes them to the enabled plugins.

## Plugins

Plugins detect technical signals and return structured data, findings, and warnings. Plugins do not write Markdown directly. They are responsible only for deterministic detection and analysis.

## Generators

Generators convert structured scan results into documentation-oriented content. This includes inventory, architecture, modules, backend, frontend, infrastructure, and snapshot narratives.

## Exporters

Exporters serialize generated content. Markdown is the functional exporter in the current baseline. DOCX and PDF modules exist as controlled placeholders for future work.

## Outputs

Configured outputs are written under `outputs/` and then copied into `latest/` and `historical/<snapshot_id>/` during snapshot creation.

## Snapshots

Snapshots capture the generated documentation state at a point in time. They support versioned historical comparison without mutating the source project.

## Latest

`latest/` represents the most recent generated documentation state and acts as the default current view for consumers.

## Manifest

`manifest.json` records the generated outputs, snapshot identifier, enabled plugins, project metadata, and DocuCore version.

## External project mode

DocuCore can read a project from one path and write documentation to a different workspace path. In this mode, DocuCore remains independent from the target repository and does not copy the project itself.

## No AI in base mode

DocuCore operates in base mode without AI. Repository scanning, plugin detection, and Markdown generation are deterministic. An optional AI enrichment layer may be added later on top of generated artifacts, but it is not part of the current baseline.

## Documentation style rule

Generated documentation should remain technical, institutional, objective, impersonal, and evidence-based. When evidence is incomplete, the wording should explicitly state the limitation and recommend manual technical validation where appropriate.
