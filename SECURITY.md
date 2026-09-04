# Security Policy

## Supported versions

Security fixes are provided for the latest released version of onot. Please
upgrade to the most recent release before reporting an issue.

| Version | Supported |
| ------- | --------- |
| 1.1.x   | ✅        |
| < 1.1   | ❌        |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues,
discussions, or pull requests.**

Instead, use GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/sktelecom/onot/security) of this
   repository.
2. Click **Report a vulnerability** and fill in the advisory form.

If you cannot use private reporting, email the maintainers listed in the
[README](README.md#maintainers) with the subject line `onot security`.

Please include:

- A description of the vulnerability and its impact.
- Steps to reproduce (a minimal SBOM or input file is very helpful).
- The onot version (`onot version`) and your OS.

## What to expect

- We aim to acknowledge a report within **5 business days**.
- We will keep you informed as we investigate and prepare a fix.
- The fix is developed in the temporary private fork GitHub creates alongside the
  draft advisory. Nothing reaches a public repository, branch, or release until the
  advisory is published, so the fix and the disclosure land together.
- Once a fix is released, we will credit you in the advisory unless you prefer to
  remain anonymous.

## Scope

onot processes SBOM documents entirely **locally** and bundles license texts so
it can run offline. Reports that are especially relevant include, but are not
limited to:

- Parsing untrusted SBOM/SPDX/CycloneDX/Excel input (e.g. XML entity expansion,
  path traversal, resource exhaustion).
- The local API sidecar (`onot-sidecar`) and the desktop app's IPC surface.
- Template rendering and PDF generation paths.
