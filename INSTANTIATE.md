# Templates — Instantiation Guide

These files are the **standard set** copied into (nearly) every new repository.

## How to scaffold a new repo

1. **Create the repo** and copy these files into it:

   ```sh
   # from your new repo's root
   cp -r /path/to/dev-setup/templates/. .
   mkdir -p docs/adr agents .github/workflows
   cp /path/to/dev-setup/.github/workflows/*.yml .github/workflows/
   cp /path/to/dev-setup/.github/dependabot.yml .github/dependabot.yml
   cp /path/to/dev-setup/docs/adr/*.md docs/adr/
   cp /path/to/dev-setup/agents/SKILLS.md agents/SKILLS.md
   ```

2. **Replace every `{{PLACEHOLDER}}`** in the copied files. The complete list:

   | Placeholder            | Where                              | Replace with                         |
   |------------------------|------------------------------------|--------------------------------------|
   | `{{REPO_NAME}}`        | README, CONTRIBUTING, SECURITY, CHANGELOG, AGENTS, Justfile | repo name            |
   | `{{REPO_DESCRIPTION}}` | README, CHANGELOG, AGENTS          | one-line description                 |
   | `{{YEAR}}`             | LICENSE, CHANGELOG                 | current year (e.g. `2026`)           |
   | `{{FULL_NAME}}`        | LICENSE                            | your legal name                      |
   | `{{EMAIL}}`            | SECURITY.md, CONTRIBUTING          | contact email for security reports   |
   | `{{VERSION}}`          | CHANGELOG                          | current version (e.g. `0.1.0`)       |
   | `{{PACKAGE_MANAGER}}`  | Justfile, workflows                | `npm`, `pip`, `cargo`, `go`, `uv`, … |
   | `{{DOCKER_IMAGE}}`     | Justfile, Dockerfile               | container image name                 |

3. **Fill in the stack-specific bits** that are intentionally left generic:
   - `Justfile` — set the actual `format` / `lint` / `build` / `test` commands.
   - `validate.yml` — the same commands run in CI via `just validate`.
   - `Dockerfile` — your base image, build steps, and runtime target.
   - `.gitignore` — uncomment/add the entries for your language and tooling.
   - `.env.example` — your real configuration variables.
   - `AGENTS.md` + `agents/SKILLS.md` — repo-specific agent instructions.

4. **Install the local hooks and tooling** (requires `just` and `pre-commit`):

   ```sh
   just install-tools     # pinned gitleaks, trufflehog, osv-scanner, pre-commit
   pre-commit install     # installs git hooks from .pre-commit-config.yaml
   ```

5. **Initialize OpenWiki** (optional, recommended for docs):

   ```sh
   openwiki --init
   ```

6. **Delete what doesn't apply.** The blueprint is a superset on purpose. If a
   repo doesn't ship a container, remove `Dockerfile`/`.dockerignore` and the
   docker recipes from `Justfile`. Keep the rest.

## Placeholder index

If you're looking at a file and aren't sure what to change, every
`{{UPPERCASE_PLACEHOLDER}}` in this directory is a required edit. After
scaffolding, run a sweep:

```sh
grep -rn '{{' . --include='*' --exclude-dir=.git
```

There should be **zero** matches when you're done.

## File-by-file

| File                     | Purpose                                                          |
|--------------------------|------------------------------------------------------------------|
| `README.md`              | project overview, badges, quickstart, links to docs              |
| `CONTRIBUTING.md`        | how to contribute: setup, commands, PR expectations              |
| `LICENSE`                | MIT license (edit `{{YEAR}}` and `{{FULL_NAME}}`)                |
| `SECURITY.md`            | supported versions + vulnerability reporting + hardening rules   |
| `CHANGELOG.md`           | Keep a Changelog format; `Unreleased` at the top                 |
| `AGENTS.md`              | root pointer: read `agents/SKILLS.md` (+ OpenWiki if enabled)    |
| `.editorconfig`          | editor defaults (indent, charset, line endings)                  |
| `.gitignore`             | base ignores; extend for your language/tooling                   |
| `.gitattributes`         | line-ending normalization + linguist hints                       |
| `.env.example`           | documented environment variables (never real values)             |
| `Dockerfile`             | generic multi-stage container template                           |
| `.dockerignore`          | keep build context small                                         |
| `.pre-commit-config.yaml`| gitleaks + trufflehog + osv-scanner + dep-age + format/lint hooks|
| `.trufflehog-excludes`   | regex exclusions for the trufflehog secret scan                  |
| `scripts/check-dep-age.py`| dependency freshness gate (all deps >= 7 days old)              |
| `Justfile`               | the single entrypoint: `install-tools`, `validate`, `security`, …|

## Placeholders in workflow files

The workflows in `.github/workflows/` reference GitHub Actions **pinned to full
commit SHAs**. When upgrading an action, change the SHA deliberately (see
`SECURITY.md` → Hardening Practices) and update the comment noting the
corresponding tag.