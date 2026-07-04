# Plugins en DocuCore

## Objetivo

Los plugins permiten extender DocuCore por stack sin contaminar el core con logica especifica de un ecosistema.

## Contrato base

Cada plugin debe heredar de `BasePlugin` e implementar:

```python
name
detect(project_root, files)
analyze(project_root, files)
```

## Reglas recomendadas

- Mantener detecciones seguras y de bajo costo.
- Preferir heuristicas simples antes que parseo avanzado.
- Devolver datos estructurados, hallazgos y advertencias.
- Evitar efectos secundarios y escritura directa de archivos.
- Mantener la redaccion documental en los generators con tono tecnico, institucional, objetivo e impersonal.

## Pasos para crear un plugin nuevo

1. Crear un archivo en `docucore/plugins/`.
2. Implementar la clase derivada de `BasePlugin`.
3. Registrar la instancia en `docucore/plugins/__init__.py`.
4. Agregar tests focalizados para la heuristica del plugin.
