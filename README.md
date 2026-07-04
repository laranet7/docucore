# DocuCore

DocuCore es un motor generico de documentacion viva para proyectos de software. El modo base funciona sin IA y genera artefactos documentales a partir de escaneo de archivos, plugins deterministicos, reglas de deteccion y generadores Markdown.

## Que es DocuCore

DocuCore analiza un repositorio, identifica tecnologias, estructura tecnica y artefactos relevantes, y genera una base documental reutilizable. El proyecto separa deteccion, generacion y exportacion para mantener un core extensible y desacoplado de proyectos concretos.

## Objetivo

- Crear una base solida para documentacion automatizada y extensible.
- Separar `core`, `plugins`, `generators`, `exporters` y `cli` desde el inicio.
- Mantener una operacion deterministica en el modo base.
- Reservar la IA como enriquecimiento opcional futuro sobre artefactos ya generados.

## Instalacion local

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

### Linux / Mac

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso basico

```bash
docucore --help
docucore init --project-name "Demo Project" --project-code "DEMO"
docucore scan
docucore build
docucore status
```

## Modo proyecto actual

Si no se especifica `--project`, DocuCore usa el directorio actual como proyecto objetivo. Si no se especifica `--output`, escribe la documentacion en `<project>/documentacion`.

Flujo recomendado:

```bash
docucore init
docucore build
docucore status
pytest
```

## Modo proyecto externo

DocuCore puede leer un repositorio objetivo y escribir la documentacion en un workspace separado.

### Windows

```bash
docucore init --project "D:\Repos\SampleProject" --output "D:\Repos\DocuCoreWorkspaces\SampleProject\docs" --project-name "Sample Project" --project-code "SAMPLE"
docucore build --project "D:\Repos\SampleProject" --output "D:\Repos\DocuCoreWorkspaces\SampleProject\docs"
docucore status --project "D:\Repos\SampleProject" --output "D:\Repos\DocuCoreWorkspaces\SampleProject\docs"
```

### Linux / Mac

```bash
docucore init --project "/home/user/repos/SampleProject" --output "/home/user/docucore-workspaces/SampleProject/docs" --project-name "Sample Project" --project-code "SAMPLE"
docucore build --project "/home/user/repos/SampleProject" --output "/home/user/docucore-workspaces/SampleProject/docs"
docucore status --project "/home/user/repos/SampleProject" --output "/home/user/docucore-workspaces/SampleProject/docs"
```

## Outputs generados

- `inventory.json`: payload estructurado del inventario tecnico.
- `inventory.md`: inventario tecnico general y hallazgos por plugin.
- `architecture.md`: lectura inicial de capas, backend, frontend e infraestructura.
- `modules.md`: modulos tecnicos y posibles modulos funcionales inferidos.
- `backend.md`: frameworks, estructura y endpoints backend detectados.
- `frontend.md`: frameworks, scripts, componentes y rutas frontend detectadas.
- `infrastructure.md`: Docker, Compose y CI/CD visibles en el repositorio.
- `manifest.json`: lista de outputs generados, plugins y metadatos del snapshot.
- `snapshot.md`: resumen versionado del conjunto documental generado.

## Snapshots y latest

Cada `build` actualiza la carpeta `latest/` con la version vigente de los artefactos habilitados y genera un snapshot historico en `historical/<snapshot_id>/`. El `manifest.json` refleja los outputs incluidos en cada corrida.

## Comandos principales

- `docucore init`: crea la estructura documental y la configuracion base.
- `docucore scan`: recorre el repositorio y genera outputs segun la configuracion.
- `docucore build`: ejecuta scan, genera documentos, actualiza `latest` y crea snapshot.
- `docucore snapshot`: versiona los outputs ya generados.
- `docucore status`: informa configuracion, latest, ultimo snapshot y outputs disponibles.

## Filosofia sin IA por defecto

DocuCore opera en modo base sin IA. La generacion documental inicial se realiza mediante escaneo de archivos, plugins deterministicos, reglas de deteccion y generadores Markdown.

## IA opcional futura

Una capa de IA puede incorporarse en el futuro como enriquecimiento opcional sobre artefactos ya generados. Esa capa no forma parte de la operacion base actual.

## Ejemplos genericos

```bash
docucore build --project "D:\Repos\SampleProject" --output "D:\Repos\DocuCoreWorkspaces\SampleProject\docs"
```

## Estructura del proyecto

```text
docucore/
core/
models/
plugins/
generators/
exporters/
```

La documentacion interna detallada vive en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PLUGINS.md](docs/PLUGINS.md), [docs/CONFIGURATION.md](docs/CONFIGURATION.md) y [docs/ROADMAP.md](docs/ROADMAP.md).
