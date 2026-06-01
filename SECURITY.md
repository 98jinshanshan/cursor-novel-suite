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

## Secrets Handling

- Never commit `.env`, `credentials.json`, or secret JSON files.
- Keep tokens in environment variables only.
- Use least-privilege keys for external providers.
