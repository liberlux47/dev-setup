# AGENTS.md

Instructions for coding agents working in this repository.

## Start here

1. **Read `agents/SKILLS.md` first.** Per-repository agent behavior, conventions,
   and workflows for this repo live there. Follow it for every task.
2. If OpenWiki is enabled, this repo has living documentation in `/openwiki`.
   Start with `openwiki/quickstart.md`, then follow links to the relevant
   architecture, workflow, domain, operation, and testing notes.

## Ground rules

- **Versions are pinned.** Never introduce floating ranges (`^`, `~`, `>=`,
  `latest`) into manifests or CI.
- **Secrets never enter the repo.** Never write real credentials into code,
  configs, or tests. Use `.env.example` placeholders and CI secret stores.
- **Match the existing style.** Run `just format` and `just lint`; follow the
  patterns already in the codebase.
- **Verify before claiming done.** Run `just validate` (format, lint, build,
  test) and `just security` (gitleaks, trufflehog, osv-scanner) on any change.

## Scope

- For per-task instructions, prefer the most specific skill in `agents/SKILLS.md`.
- This file is intentionally short: it delegates to `agents/SKILLS.md` so agent
  behavior stays centralized and version-controlled in one place.