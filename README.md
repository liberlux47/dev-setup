# Dev Setup Blueprint

A reusable starter kit for scaffolding new development projects. This repository
holds the standard documents, templates, workflows, and conventions applied to
(nearly) every repository going forward.

> **Current status: blueprint.** This is a canonical reference. To bootstrap a new
> repo, follow the [instantiation guide](INSTANTIATE.md).

---

## Repository layout

```
dev-setup/
├── README.md                    ← you are here (blueprint index)
├── Justfile                     ← tooling for THIS repo (install-tools, etc.)
├── agents/
│   └── SKILLS.md                ← per-repo agent instructions (see below)
├── docs/
│   └── adr/
│       ├── README.md            ← ADR index + usage guidance
│       └── TEMPLATE.md          ← ADR template (used for rare, significant decisions)
├── templates/                   ← copy these into new repos
│   ├── README.md                ← instantiation guide + placeholder index
│   ├── CONTRIBUTING.md
│   ├── LICENSE                  ← MIT
│   ├── SECURITY.md
│   ├── CHANGELOG.md
│   ├── AGENTS.md
│   ├── .editorconfig
│   ├── .gitignore
│   ├── .gitattributes
│   ├── .env.example
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .pre-commit-config.yaml
│   └── Justfile
└── .github/
    ├── dependabot.yml
    └── workflows/
        ├── validate.yml        ← lint, format, build, unit + integration tests
        ├── security.yml        ← gitleaks, trufflehog, osv-scanner
        └── docs.yml            ← doc build on release/production deploy
```

## Conventions

These are the ground rules that apply to every repo scaffolded from this blueprint.

### Versions are pinned, never floating

- **Dependencies**: exact versions in manifests; commit lockfiles
  (`package-lock.json`, `requirements.txt`, `go.sum`, `Cargo.lock`, …).
- **No floating ranges**: no `^`, `~`, `>=`, `*`, or `latest` in dependency specs.
- **GitHub Actions**: pinned to full commit SHAs — never mutable tags like `@v4`.
  (Each workflow file includes a comment noting the SHA it pins and the tag it
  corresponds to, so upgrading is a deliberate, reviewed change.)
- **Local tooling** (`Justfile` → `install-tools`): pinned to exact released versions.

### Security is a workflow, not a feature

- `validate.yml` — gate for lint/format/build/test on every push and PR.
- `security.yml` — gitleaks (secrets) + trufflehog (secrets, verified) on push/PR,
  plus a weekly osv-scanner (dependency vulnerabilities) sweep.
- `pre-commit-config.yaml` — same secret/vuln checks run locally before anything
  reaches CI.
- `SECURITY.md` — documents supported versions and how to report a vulnerability.

### Architecture decisions are rare and deliberate

`docs/adr/` holds **Architecture Decision Records** for architecturally
significant decisions only — the kind that shape the system and are hard to
reverse. Architecture is expected to be designed *before* coding starts; ADRs
capture the few decisions worth memorializing and their reasoning. Day-to-day
implementation choices do **not** belong in ADRs.

### Agent behavior is per-repo, centralized in `agents/SKILLS.md`

Coding agents working in a repo should read the repository's `agents/SKILLS.md`
for how to behave in that repo. The root `AGENTS.md` (scaffolded from
`templates/AGENTS.md`) points agents there. If a repo uses OpenWiki, the root
`AGENTS.md` also points to the wiki.

## Getting started

Tools used by this blueprint (see `Justfile` → `install-tools` for the pinned
versions):

| Tool         | Purpose                                     |
|--------------|---------------------------------------------|
| `just`       | command runner (local dev + CI entrypoint)  |
| `pre-commit` | local git hooks runner                      |
| `gitleaks`   | secret scanning (CI + pre-commit)           |
| `trufflehog` | secret scanning, verified (CI + pre-commit) |
| `osv-scanner`| dependency vulnerability scanning           |
| `openwiki`   | agent wiki/docs generation (optional)       |

To install everything this blueprint expects on a fresh machine:

```sh
just install-tools
```

## License

This blueprint is provided under the MIT License — see
[`templates/LICENSE`](templates/LICENSE). Each project scaffolded from it applies
its own MIT license.