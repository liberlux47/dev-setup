# Contributing to {{REPO_NAME}}

Thanks for taking the time to contribute!

## Ground rules

- **Versions are pinned.** Dependency manifests use exact versions; lockfiles are
  committed. No `^`, `~`, `>=`, `*`, or `latest`. GitHub Actions are pinned to
  full commit SHAs.
- **Secrets never enter this repo.** Run `pre-commit` (gitleaks + trufflehog)
  locally; CI enforces the same checks.
- **Tests are expected.** New code should ship with unit and/or integration tests,
  and everything must pass `just validate` before merge.

## Getting started

```sh
# 1. Install pinned local tooling
just install-tools

# 2. Install git hooks (gitleaks, trufflehog, osv-scanner, format, lint)
pre-commit install

# 3. Run the full gate locally
just validate
```

## Development workflow

1. **Branch.** Work on a feature branch (`feat/...`, `fix/...`).
2. **Commit.** Use [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`, `ci:`.
3. **Format & lint.** `just format` and `just lint` — keep the diff clean.
4. **Test.** `just test`. Add tests for changes and fixes.
5. **Build.** `just build` — make sure the app still compiles.
6. **Push & open a PR.** CI runs `validate.yml` and `security.yml` automatically.

## Commit message format

```
<type>(<scope>): <subject>

<body>
```

Examples:

```
feat(auth): add refresh-token rotation
fix(api): return 409 on duplicate resource
docs: clarify environment variable table
```

## Pull request checklist

- [ ] `just validate` passes (format, lint, build, test)
- [ ] `pre-commit` passes (gitleaks, trufflehog, osv-scanner)
- [ ] New/changed behavior covered by tests
- [ ] `CHANGELOG.md` updated under `Unreleased` if user-facing
- [ ] No `{{PLACEHOLDER}}` left in code or docs

## Reporting bugs

Open an issue with:

- Steps to reproduce
- Expected vs. actual behavior
- Environment (OS, versions, branch/commit)

For security issues, **do not open a public issue** — see [SECURITY.md](SECURITY.md).