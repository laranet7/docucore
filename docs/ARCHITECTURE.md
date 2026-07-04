# Arquitectura de DocuCore

## Vision general

DocuCore separa la captura de datos tecnicos de la narrativa documental. El scanner y los plugins detectan estructura y hallazgos; luego los generators y exporters convierten esos datos en salidas reutilizables.

## Capas

### Core generico

La carpeta `docucore/core` concentra configuracion, recorrido de archivos, manifest, snapshots, estado y escritura de outputs. Esta capa no depende de stacks concretos ni de IA.

### Plugins

La carpeta `docucore/plugins` encapsula detecciones por tecnologia. Cada plugin recibe el root del proyecto y la lista de archivos ya filtrados. Debe devolver datos estructurados, hallazgos y advertencias.

### Generators

La carpeta `docucore/generators` transforma resultados crudos de scan en modelos documentales reutilizables, como inventarios y snapshots.

### Exporters

La carpeta `docucore/exporters` decide como serializar los modelos. En esta iteracion Markdown es funcional y DOCX/PDF son placeholders controlados.

### CLI

La CLI orquesta el flujo de trabajo con comandos pequenos y claros: `init`, `scan`, `build`, `snapshot` y `status`.

## Flujo de ejecucion

1. `init` crea estructura y configuracion base.
2. `scan` carga config, recorre archivos y ejecuta plugins.
3. `build` combina scan, inventario, snapshot, latest y manifest.
4. `snapshot` versiona outputs existentes.
5. `status` inspecciona el estado documental del proyecto.

## Separacion entre datos y narrativa

Los plugins nunca generan Markdown directamente. Primero producen datos estructurados. Luego los generators consolidan esos datos y los exporters producen la capa documental final.

## Regla de estilo documental

Los documentos generados por DocuCore deben mantener una redaccion tecnica, institucional, objetiva e impersonal. La narrativa debe apoyarse en evidencia detectada automaticamente y evitar formulaciones subjetivas o centradas en el autor. Cuando la evidencia sea parcial, la redaccion debe usar lenguaje prudente y explicitar la necesidad de validacion tecnica manual.
