# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | ✅ (active)        |
| older   | ❌ (upgrade first) |

## Reporting a Vulnerability

**Do not open a public issue or PR.** Security issues are handled privately.

- Email: **{{EMAIL}}**
- Include: affected version, a minimal reproduction, and your suggested fix if
  you have one.
- You should receive an acknowledgement within **48 hours**.
- We coordinate a fix before public disclosure.

## Hardening Practices (enforced in this repo)

This repository applies the following rules. CI and local hooks
(`.pre-commit-config.yaml`) enforce them.

### 1. Exact dependency versions — no floating versions

- Manifests pin **exact versions**. Floating ranges (`^`, `~`, `>=`), wildcards
  (`*`), and `latest` are prohibited.
- **Lockfiles are committed** (`package-lock.json`, `requirements.txt`, `go.sum`,
  `Cargo.lock`, …) so builds are reproducible.
- Dependency updates land as deliberate PRs (Dependabot) and are reviewed before
  merge.

### 2. GitHub Actions pinned to full commit SHAs

- Every action in `.github/workflows/` is pinned to a **full commit SHA** —
  never a mutable tag like `@v4`.
- Upgrading an action is a deliberate change: update the SHA and the comment
  recording the corresponding tag.

### 3. Secrets never enter the repository

- Real values live in CI secret stores or local tooling, **never** in source.
- `.env.example` documents variables with placeholder values only.
- Secret scanning runs on every push and PR via **gitleaks** and **trufflehog**
  (CI: `security.yml`; local: pre-commit hooks).

### 4. Dependencies scanned for known vulnerabilities

- **osv-scanner** runs on a weekly schedule and on push/PR (CI: `security.yml`;
  local: pre-commit hook) and fails the build on known vulnerabilities.
- **Dependabot** opens update PRs so vulnerable dependencies are patched
  promptly.

### 5. Containers follow the same rules

- `Dockerfile` uses pinned base image digests where feasible, never `latest`.
- `.dockerignore` keeps the build context minimal.

## Scope

This policy covers the repository itself and the software it ships. For
vulnerabilities in third-party dependencies, apply the upstream advisory via the
OSV database.