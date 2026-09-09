# {{REPO_NAME}}

{{REPO_DESCRIPTION}}

## Quickstart

```sh
# install pinned local tooling (just, pre-commit, gitleaks, trufflehog, osv-scanner)
just install-tools
pre-commit install

# run everything
just validate
```

## Development

```sh
just format     # format code
just lint       # lint code
just build      # build the app
just test       # unit + integration tests
just security   # gitleaks + trufflehog + osv-scanner
```

`just validate` runs format, lint, build, and test in sequence — the same gates
enforced by the `validate.yml` workflow in CI.

## Documentation

- [Architecture Decision Records](docs/adr/README.md) — rare, significant design
  decisions and their rationale.
- If OpenWiki is enabled: `openwiki/` holds the living repo wiki.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md) for supported versions and how to report a
vulnerability.

## License

MIT — see [LICENSE](LICENSE).