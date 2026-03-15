#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import CONFIG_SYNC_SOURCES, fingerprint, listed_generated_files, resolve_repo_root, skill_dir, source_fingerprint_from_sync


REQUIRED_CURATED = [
    "decision-guide.md",
    "checklists.md",
    "anti-patterns.md",
    "update-playbook.md",
]

REQUIRED_GENERATED = [
    "doc-catalog.generated.md",
    "config-matrix.generated.md",
    "sync-status.generated.md",
]

REQUIRED_PLATFORM_TOKENS = [
    "android_sqlite",
    "multiplatform_sqlite",
    "native_sqlite",
    "jvm_sqlite",
    "js_sqlite",
    "jvm_mysql",
    "jvm_postgresql",
    "jvm_h2",
]

REQUIRED_DRIVER_TOKENS = [
    "android-driver",
    "native-driver",
    "sqlite-driver",
    "web-worker-driver",
    "jdbc-driver",
]


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(skill_root: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    references = skill_root / "references"

    for filename in REQUIRED_CURATED + REQUIRED_GENERATED:
        ensure((references / filename).exists(), f"Missing references/{filename}", errors)

    skill_md = skill_root / "SKILL.md"
    agents_yaml = skill_root / "agents" / "openai.yaml"
    ensure(skill_md.exists(), "Missing SKILL.md", errors)
    ensure(agents_yaml.exists(), "Missing agents/openai.yaml", errors)

    if agents_yaml.exists():
        agents_text = agents_yaml.read_text()
        ensure('default_prompt: "Use $sqldelight ' in agents_text, "agents/openai.yaml default_prompt must mention $sqldelight", errors)

    doc_catalog_path = references / "doc-catalog.generated.md"
    if doc_catalog_path.exists():
        doc_text = doc_catalog_path.read_text()
        ensure("| Section | Page | Intent | Official latest URL | Local source path | Topic tags |" in doc_text, "Doc catalog table header is missing", errors)
        urls = re.findall(r"https://sqldelight\.github\.io/sqldelight/latest/[^\s|]+", doc_text)
        ensure(bool(urls), "Doc catalog must contain official latest URLs", errors)
        for token in REQUIRED_PLATFORM_TOKENS:
            ensure(token in doc_text, f"Doc catalog is missing platform token {token}", errors)

    config_path = references / "config-matrix.generated.md"
    if config_path.exists():
        config_text = config_path.read_text()
        for heading in ("## Driver Matrix", "## Dialect Modules", "## Core Gradle Options"):
            ensure(heading in config_text, f"Config matrix is missing heading {heading}", errors)
        for token in REQUIRED_DRIVER_TOKENS:
            ensure(token in config_text, f"Config matrix is missing driver token {token}", errors)

    sync_path = references / "sync-status.generated.md"
    if sync_path.exists():
        sync_text = sync_path.read_text()
        sync_fingerprint = source_fingerprint_from_sync(sync_text)
        expected_fingerprint = fingerprint(repo_root, CONFIG_SYNC_SOURCES)
        ensure(sync_fingerprint == expected_fingerprint, "sync-status fingerprint does not match the current repo sources", errors)
        generated_files = listed_generated_files(sync_text)
        for required in [f"references/{name}" for name in REQUIRED_GENERATED]:
            ensure(required in generated_files, f"sync-status is missing generated file entry {required}", errors)
            ensure((skill_root / required).exists(), f"sync-status references missing file {required}", errors)

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the SQLDelight skill references.")
    parser.add_argument("--repo-root", help="Path to a sqldelight repository checkout.")
    parser.add_argument("--skill-dir", help="Path to the sqldelight skill directory.")
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.repo_root)
    skill_root = skill_dir(args.skill_dir)
    errors = validate(skill_root, repo_root)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        raise SystemExit(1)
    print("[OK] SQLDelight references are valid")


if __name__ == "__main__":
    main()
