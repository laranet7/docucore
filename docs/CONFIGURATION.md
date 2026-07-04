# Configuracion

DocuCore usa `project.config.json` para definir el proyecto objetivo que se lee y el destino documental que se escribe. Por defecto vive en `documentacion/config/project.config.json`, pero tambien puede vivir en un workspace externo.

## Campos principales

- `project_name`: nombre legible del proyecto.
- `project_code`: codigo corto del proyecto.
- `language`: idioma principal de la documentacion.
- `root_path`: proyecto objetivo leido por el scanner.
- `documentation_path`: destino documental escrito por DocuCore.
- `include_paths`: rutas a recorrer.
- `exclude_paths`: rutas o carpetas a ignorar.
- `enabled_plugins`: plugins habilitados.
- `outputs`: tipos de salida habilitados.
- `exporters`: exportadores habilitados.
- `ai.enabled`: bandera reservada para una capa futura opcional.

## Ejemplo

```json
{
  "project_name": "Unnamed Project",
  "project_code": "UNNAMED",
  "language": "es",
  "root_path": "D:/Repos/SampleProject",
  "documentation_path": "D:/Repos/DocuCoreWorkspaces/SampleProject/docs",
  "include_paths": ["."],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "node_modules"
  ],
  "enabled_plugins": ["generic", "python", "node", "dotnet", "docker"],
  "outputs": [
    "inventory",
    "architecture",
    "modules",
    "backend",
    "frontend",
    "infrastructure",
    "snapshot"
  ],
  "exporters": ["markdown"],
  "ai": {
    "enabled": false
  }
}
```

## Reglas de uso

- `init` crea este archivo si no existe.
- `scan`, `build`, `snapshot` y `status` lo usan como fuente de verdad.
- `--config` permite apuntar a una ruta distinta cuando sea necesario.
- `root_path` y `documentation_path` pueden ser absolutos o relativos, pero DocuCore los resuelve internamente como rutas absolutas.
- Si se usan `--project` o `--output`, esos argumentos CLI tienen prioridad sobre lo definido en la configuracion.
- Cuando `documentation_path` esta dentro de `root_path`, DocuCore excluye automaticamente esa carpeta del escaneo para no documentar sus propios outputs.
- `outputs` controla que documentos se generan. Configuraciones antiguas con solo `inventory` y `snapshot` siguen siendo validas.

## Diferencia entre lectura y escritura

- `root_path` representa el repositorio fuente que se analiza.
- `documentation_path` representa el workspace documental donde se generan `config/`, `outputs/`, `historical/` y `latest/`.
- Ambos paths pueden apuntar al mismo proyecto o a ubicaciones completamente separadas.
