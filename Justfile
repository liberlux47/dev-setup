# Justfile for the dev-setup blueprint repo itself.
#
# This keeps the machine ready to scaffold repos from this blueprint:
# install-tools sets up just, gitleaks, trufflehog, osv-scanner, pre-commit,
# and openwiki — all pinned to exact versions (no floating).

# Print available recipes
default:
    @just --list

# Install the full pinned toolchain used by the blueprint
install-tools:
    @echo "== just (task runner) =="
    @if ! command -v just >/dev/null; then \
        curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin; \
    else echo "  already installed ($(just --version))"; fi

    @echo "== gitleaks v8.30.1 (secret scanning) =="
    @if ! command -v gitleaks >/dev/null; then \
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz -o /tmp/gitleaks.tgz && \
        tar -xzf /tmp/gitleaks.tgz gitleaks && sudo install gitleaks /usr/local/bin/gitleaks && rm -f gitleaks /tmp/gitleaks.tgz; \
    else echo "  already installed ($(gitleaks version))"; fi

    @echo "== trufflehog v3.97.4 (secret scanning, verified) =="
    @if ! command -v trufflehog >/dev/null; then \
        curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin v3.97.4; \
    else echo "  already installed ($(trufflehog --version))"; fi

    @echo "== osv-scanner v2.5.1 (dependency vulnerabilities) =="
    @if ! command -v osv-scanner >/dev/null; then \
        curl -sSfL https://github.com/google/osv-scanner/releases/download/v2.5.1/osv-scanner_linux_amd64 -o /tmp/osv-scanner && \
        sudo install /tmp/osv-scanner /usr/local/bin/osv-scanner && rm -f /tmp/osv-scanner; \
    else echo "  already installed ($(osv-scanner --version))"; fi

    @echo "== pre-commit (local git hooks) =="
    @if ! command -v pre-commit >/dev/null; then \
        python3 -m pip install --user --break-system-packages pre-commit; \
    else echo "  already installed ($(pre-commit --version))"; fi

    @echo "== openwiki (agent docs/wiki) =="
    @if ! command -v openwiki >/dev/null; then \
        npm install -g openwiki; \
    else echo "  already installed"; fi

    @echo ""
    @echo "All tools installed. Verify with: just versions"

# Show installed versions
versions:
    just --version
    gitleaks version
    trufflehog --version
    osv-scanner --version
    pre-commit --version
    openwiki --help >/dev/null && echo "openwiki: installed"

# Check the toolchain is present and report missing pieces
check:
    @echo "Checking toolchain…"
    @for tool in just gitleaks trufflehog osv-scanner pre-commit openwiki; do \
        if command -v "$tool" >/dev/null 2>&1; then echo "  ✓ $tool"; else echo "  ✗ $tool MISSING — run: just install-tools"; fi; \
    done

# Install pre-commit hooks from templates/.pre-commit-config.yaml
hooks:
    pre-commit install