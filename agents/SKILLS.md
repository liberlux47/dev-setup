# Agent Skills — Per-Repository Agent Instructions

This file is the **central, per-repository instruction set for coding agents**
working in this repo. The root `AGENTS.md` points agents here.

These are conventions and expectations an agent must follow for **every** task,
regardless of scope. Repo-specific details (stack, layout, commands) belong here;
generic agent guidance lives in the agent's own configuration.

## 1. Read the context first

Before making any change:

1. Read `AGENTS.md` at the repo root (and follow any OpenWiki pointer if present).
2. Read this file fully.
3. Run `just` to see the available recipes, and read `Justfile` to understand the
   canonical commands for this repo.
4. Inspect existing code structure and patterns; match them. Do not invent new
   patterns when established ones exist.

## 2. Non-negotiable rules

These mirror `SECURITY.md` and `CONTRIBUTING.md` — an agent must not bypass them:

- **Pinned versions only.** Never introduce floating ranges (`^`, `~`, `>=`,
  `*`, `latest`) into dependency manifests or CI. Keep lockfiles committed.
- **Never write secrets.** Real credentials, keys, or tokens never belong in
  code, tests, or config. Use `.env.example` placeholders and CI secret stores.
- **Run the gates before finishing.** `just validate` (format, lint, build, test)
  and `just security` (gitleaks, trufflehog, osv-scanner) must pass.
- **Match house style.** Follow existing formatting, naming, and structure.

## 3. Task workflow

1. **Plan** — state what you'll change and why, especially if it touches
   architecture.
2. **Implement** — smallest change that satisfies the task; prefer editing
   existing files over creating new ones.
3. **Verify** — run the relevant recipes (`just test`, `just build`, etc.) and
   confirm before declaring completion.
4. **Report** — summarize what changed, how it was verified, and anything unusual.

## 4. Documentation responsibilities

- Update `CHANGELOG.md` under `Unreleased` for user-facing changes.
- If behavior or configuration changes, update `README.md`, `.env.example`, or
  docs accordingly.
- Architecture-significant decisions: propose an ADR in `docs/adr/` (use
  `TEMPLATE.md`). Only for rare, significant decisions — see `docs/adr/README.md`.

## 5. Security-responsible behavior

- If you detect a leaked secret in the codebase or history, **do not** print it,
  commit around it silently, or include it in reports verbatim. Flag it to the
  maintainer privately (see `SECURITY.md`).
- If osv-scanner reports a vulnerable dependency, do not upgrade with a floating
  version — propose the exact fixed version.

## 6. Scope boundary

This file defines *behavior*. For how to use tools, the local dev loop, and
per-tool commands, follow `Justfile` and this repo's docs (`openwiki/` if
enabled, `docs/` otherwise).