# Security Policy

## Supported versions

The project currently supports the latest public baseline on the default branch. Older snapshots or unpublished local variants are not covered by this policy.

## Reporting a vulnerability

Please open a private security advisory if available, or contact the repository maintainer through GitHub.

## Sensitive information

Do not publish:

- secrets
- tokens
- `.env` files
- private customer documentation
- local machine paths
- generated outputs that expose internal infrastructure details

## Generated documentation warning

DocuCore can generate documentation from real repositories. Review generated artifacts before sharing them publicly. Generated files may contain service names, paths, ports, environment variable names, or other operational details that should remain private.
