# Plugins

## Purpose

Plugins extend DocuCore by stack or technology without contaminating the core execution layer with project-specific rules.

## Base contract

Each plugin should inherit from `BasePlugin` and implement:

```python
name
detect(project_root, files)
analyze(project_root, files)
```

## Responsibilities

- Detect technical signals using deterministic rules
- Return structured data, findings, and warnings
- Remain safe and low-cost during execution
- Avoid side effects outside their own in-memory analysis

## Structured output

Plugins should provide:

- `detected`
- `technologies`
- `findings`
- `warnings`
- `data`

The `data` payload is the main handoff to generators.

## Warnings

Warnings should be factual and precise. For example:

- missing parseable metadata files
- fallback parsing being used
- limited evidence for a conclusion

Warnings should not exaggerate risk or quality if the evidence is incomplete.

## No direct Markdown writing

Plugins must not write Markdown directly. Markdown generation belongs to the generator layer so that detection and narrative remain cleanly separated.

## Creating a new plugin

1. Add a file under `docucore/plugins/`.
2. Implement the plugin class from `BasePlugin`.
3. Return structured results from `analyze`.
4. Register the plugin in `docucore/plugins/__init__.py`.
5. Add focused tests that validate the detection heuristics.

## Documentation style

If plugin findings are surfaced in generated documents, the wording should remain technical, institutional, objective, impersonal, and evidence-based.
