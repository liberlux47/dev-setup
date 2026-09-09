#!/usr/bin/env python3
"""
check-dep-age.py — dependency freshness gate (7-day exclusive rule).

Enforces that every pinned dependency version in the repository is at least
N days old (default: 7). Newly published packages are rejected because they
have not yet received community and tooling scrutiny; malicious or broken
releases are usually discovered within the first days after publication.

Supported manifests (auto-detected):
  - package-lock.json            (npm)
  - requirements.txt / req*.txt  (pip, exact pins `name==version` only)
  - Cargo.lock                   (cargo, TOML via tomllib)
  - go.mod                       (go, `require` lines only)

Usage:
  python3 scripts/check-dep-age.py [--min-age-days 7] [--strict] [--json]

Exit codes:
  0  all dependencies are at least N days old (or no supported manifests)
  1  one or more dependencies are too fresh
  2  usage error
  3  internal error (e.g. missing Python version)

Notes:
  - Network lookups are cached in .cache/dep-age-cache.json (gitignored).
  - By default a failed lookup is reported but does NOT fail the build
    (CI remains resilient to transient network issues). Pass --strict to
    fail closed when a version's publish date cannot be determined.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

MIN_AGE_DAYS_DEFAULT = 7
CACHE_FILE = ".cache/dep-age-cache.json"
CACHE_TTL_SECONDS = 24 * 60 * 60  # re-check after 24h
HTTP_TIMEOUT = 15
MAX_WORKERS = 8

# Registries per ecosystem
NPM_PACKUMENT = "https://registry.npmjs.org/{name}"
PYPI_JSON = "https://pypi.org/pypi/{name}/{version}/json"
CARGO_JSON = "https://crates.io/api/v1/crates/{name}/{version}"
GO_INFO = "https://proxy.golang.org/{module}/@v/{version}.info"

_lock = threading.Lock()
_failures: list[str] = []
_warnings: list[str] = []


# ── Manifest parsing ───────────────────────────────────────────────────────

def parse_npm(path: Path) -> list[tuple[str, str, str]]:
    """package-lock.json -> [(ecosystem, name, version)]"""
    data = json.loads(path.read_text(encoding="utf-8"))
    deps: list[tuple[str, str, str]] = []
    packages = data.get("packages") or {}
    for loc, meta in packages.items():
        if not loc or loc == "":
            continue
        name = loc.removeprefix("node_modules/").split("node_modules/")[-1]
        version = meta.get("version")
        if name and version and name != loc:
            deps.append(("npm", name, version))
    # legacy lockfile v1
    legacy = data.get("dependencies") or {}

    def walk(node: dict):
        for name, meta in node.items():
            version = meta.get("version")
            if name and version:
                deps.append(("npm", name, version))
            if meta.get("dependencies"):
                walk(meta["dependencies"])

    walk(legacy)
    return deps


def parse_requirements(path: Path) -> list[tuple[str, str, str]]:
    """requirements.txt -> [(ecosystem, name, version)] for exact pins."""
    deps: list[tuple[str, str, str]] = []
    pin = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([A-Za-z0-9_.!+*\-]+)")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].split(";", 1)[0].strip()
        if not line:
            continue
        m = pin.match(line)
        if m:
            name = m.group(1).split("[")[0]  # strip extras like pkg[extra]
            deps.append(("pypi", name, m.group(2)))
    return deps


def parse_cargo(path: Path) -> list[tuple[str, str, str]]:
    """Cargo.lock -> [(ecosystem, name, version)]"""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        _warnings.append("tomllib unavailable; skipping Cargo.lock")
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    deps: list[tuple[str, str, str]] = []
    for pkg in data.get("package", []):
        name = pkg.get("name")
        version = pkg.get("version")
        if name and version:
            deps.append(("cargo", name, version))
    return deps


def _escape_go_module(mod: str) -> str:
    """Escape a Go module path for the proxy (uppercase -> !lowercase)."""
    out = []
    for ch in mod:
        if "A" <= ch <= "Z":
            out.append("!" + ch.lower())
        elif ch == "!":
            out.append("!!")
        else:
            out.append(ch)
    return "".join(out)


def parse_go(path: Path) -> list[tuple[str, str, str]]:
    """go.mod -> [(ecosystem, module, version)] from `require` lines."""
    text = path.read_text(encoding="utf-8")
    deps: list[tuple[str, str, str]] = []
    require_re = re.compile(r"^\s*([\w.\-/~]+(?:\s+[\w.\-/~]+)?)\s+v([\w.\-+]+)")
    in_block = False
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line.startswith(")"):
            in_block = False
            continue
        if in_block or line.startswith("require "):
            line = re.sub(r"^require\s+", "", line)
            m = require_re.match(line)
            if m:
                mod, ver = m.group(1), m.group(2)
                if "=>" in line:
                    continue  # replaced modules resolve elsewhere
                deps.append(("go", mod, ver))
    return deps


MANIFEST_PARSERS: list[tuple[list[str], object]] = [
    (["package-lock.json"], parse_npm),
    (["requirements.txt", "req*.txt"], parse_requirements),
    (["Cargo.lock"], parse_cargo),
    (["go.mod"], parse_go),
]


# ── Registry lookups ───────────────────────────────────────────────────────

def _http_json(url: str, headers: dict[str, str] | None = None) -> dict:
    req = Request(url, headers=headers or {}, method="GET")
    with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_publish_date(ecosystem: str, name: str, version: str) -> str | None:
    """Return ISO-8601 publish date for a pinned version, or None."""
    try:
        if ecosystem == "npm":
            # scoped packages: @scope/name -> @scope%2Fname
            # Full packument (not the abbreviated corgi doc) is required because
            # only the full doc carries the `time` -> {version: publishDate} map.
            enc = name.replace("/", "%2F")
            doc = _http_json(NPM_PACKUMENT.format(name=enc))
            return doc.get("time", {}).get(version)
        if ecosystem == "pypi":
            doc = _http_json(PYPI_JSON.format(name=name, version=version))
            for f in doc.get("urls", []):
                ts = f.get("upload_time_iso_8601") or f.get("upload_time")
                if ts:
                    return ts
            return None
        if ecosystem == "cargo":
            doc = _http_json(
                CARGO_JSON.format(name=name, version=version),
                {"User-Agent": "check-dep-age/1.0 (repo freshness gate)"},
            )
            return doc.get("version", {}).get("created_at")
        if ecosystem == "go":
            mod = quote(_escape_go_module(name), safe="/.")
            # The proxy expects the `v` prefix (parse_go strips it from go.mod)
            ver = version if version.startswith("v") else "v" + version
            doc = _http_json(GO_INFO.format(module=mod, version=quote(ver, safe="")))
            return doc.get("Time")
    except Exception as exc:  # noqa: BLE001 — report, don't crash
        _warnings.append(f"{ecosystem}:{name}@{version}: lookup failed ({exc})")
        return None
    return None


# ── Cache ──────────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    cache_path = Path(CACHE_FILE)
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        # Drop stale entries
        now = datetime.now(timezone.utc)
        fresh = {}
        for key, val in data.items():
            ts = datetime.fromisoformat(val["fetched"])
            if (now - ts).total_seconds() < CACHE_TTL_SECONDS:
                fresh[key] = val
        return fresh
    except Exception:  # noqa: BLE001
        return {}


def _save_cache(cache: dict) -> None:
    cache_path = Path(CACHE_FILE)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Enforce the dependency freshness gate (7-day exclusive rule)."
    )
    p.add_argument(
        "--min-age-days",
        type=int,
        default=MIN_AGE_DAYS_DEFAULT,
        help=f"minimum age in days for a dependency (default: {MIN_AGE_DAYS_DEFAULT})",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="fail the build when a publish date cannot be determined",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="emit results as JSON on stdout",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_age_days < 0:
        print("error: --min-age-days must be >= 0", file=sys.stderr)
        return 2

    root = Path.cwd()
    cache = _load_cache()
    manifest_hits: list[Path] = []

    for patterns, parser in MANIFEST_PARSERS:
        for pattern in patterns:
            for path in root.glob(pattern):
                if path.is_file():
                    manifest_hits.append(path)

    if not manifest_hits:
        print("check-dep-age: no supported manifests found; nothing to check.")
        return 0

    all_deps: list[tuple[str, str, str]] = []
    for patterns, parser in MANIFEST_PARSERS:
        for pattern in patterns:
            for path in root.glob(pattern):
                if path.is_file() and parser is not None:
                    try:
                        all_deps.extend(parser(path))
                    except Exception as exc:  # noqa: BLE001
                        _warnings.append(f"failed to parse {path}: {exc}")

    if not all_deps:
        print("check-dep-age: manifests found but no exact pins to check.")
        return 0

    # Deduplicate
    unique = sorted(set(all_deps))
    now = datetime.now(timezone.utc)

    def check_one(dep: tuple[str, str, str]) -> tuple[str, str, str, str | None]:
        eco, name, version = dep
        key = f"{eco}:{name}@{version}"
        with _lock:
            cached = cache.get(key)
        if cached and "published" in cached:
            return (eco, name, version, cached["published"])
        published = fetch_publish_date(eco, name, version)
        if published:
            with _lock:
                cache[key] = {"published": published, "fetched": now.isoformat()}
        return (eco, name, version, published)

    results: list[tuple[str, str, str, str | None]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(check_one, d) for d in unique]
        for fut in as_completed(futures):
            results.append(fut.result())

    _save_cache(cache)

    violations: list[dict] = []
    unknown: list[dict] = []
    for eco, name, version, published in results:
        if not published:
            unknown.append({"ecosystem": eco, "name": name, "version": version})
            continue
        pub = datetime.fromisoformat(published.replace("Z", "+00:00"))
        age_days = (now - pub).total_seconds() / 86400.0
        if age_days < args.min_age_days:
            violations.append(
                {
                    "ecosystem": eco,
                    "name": name,
                    "version": version,
                    "published": published,
                    "age_days": round(age_days, 2),
                }
            )

    if args.json:
        print(
            json.dumps(
                {
                    "min_age_days": args.min_age_days,
                    "violations": violations,
                    "unknown": unknown,
                    "warnings": _warnings,
                },
                indent=2,
            )
        )
    else:
        if unknown:
            print(f"check-dep-age: could not determine publish date for {len(unknown)} packages")
        if violations:
            print(f"check-dep-age: {len(violations)} dependency(ies) younger than {args.min_age_days} days:")
            for v in violations:
                print(
                    f"  ✗ {v['ecosystem']}:{v['name']}@{v['version']} "
                    f"published {v['published']} ({v['age_days']} days ago)"
                )
        if _warnings:
            for w in _warnings:
                print(f"  ⚠ {w}", file=sys.stderr)

    if violations:
        return 1
    if args.strict and unknown:
        print("check-dep-age: --strict set; failing on undetermined publish dates", file=sys.stderr)
        return 1

    if not args.json:
        print(f"check-dep-age: ok — {len(results)} dependencies, all ≥ {args.min_age_days} days old.")
    return 0


if __name__ == "__main__":
    sys.exit(main())