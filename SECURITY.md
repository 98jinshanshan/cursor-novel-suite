# Security Policy

## Supported Scope

This repository contains tooling and templates for novel generation and video rendering.
Security-relevant areas include:

- command execution in CLI wrappers
- local file path handling
- environment variable and API key usage
- third-party service integrations

## Reporting a Vulnerability

If you discover a vulnerability, do not open a public issue with exploit details.

Please report privately with:

- affected path(s)
- reproduction steps
- impact assessment
- proposed mitigation (if available)

After receiving a report, maintainers should:

1. reproduce and confirm impact
2. prepare a fix in a private branch
3. publish the patch and changelog note
4. disclose details after fix rollout

## Security audits

Periodic static reviews are documented under `docs/audit/`. Latest Python review:
[docs/audit/2026-06-04-python-security-audit.md](docs/audit/2026-06-04-python-security-audit.md).

**2026-06-04 remediations:** MCP path guard, chapter `--input` bounds (project + system temp),
`openai_image` HTTPS allowlist + download caps, graphify token sanitization, `intel_scan` HTML size cap,
`zip-refresh` GitHub-only URL validation, CI `pip-audit` + `bandit`.

## MCP deployment

- Use Cursor/local **stdio** MCP only.
- Do **not** expose `cursor-novel-video/mcp/server.py` on a network without authentication.

## Secrets Handling

- Never commit `.env`, `credentials.json`, or secret JSON files.
- Keep tokens in environment variables only.
- Use least-privilege keys for external providers.
