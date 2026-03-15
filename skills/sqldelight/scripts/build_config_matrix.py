#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import (
    collect_artifacts,
    constructors_in,
    parse_frontmatter,
    render_includes,
    resolve_repo_root,
    skill_dir,
    unique,
    write_sync_status,
)


PLATFORM_DOCS = [
    ("SQLite (Android)", "docs/android_sqlite/index.md"),
    ("SQLite (Multiplatform)", "docs/multiplatform_sqlite/index.md"),
    ("SQLite (Native)", "docs/native_sqlite/index.md"),
    ("SQLite (JVM)", "docs/jvm_sqlite/index.md"),
    ("SQLite (JS)", "docs/js_sqlite/index.md"),
    ("MySQL (JVM)", "docs/jvm_mysql/index.md"),
    ("PostgreSQL (JVM)", "docs/jvm_postgresql/index.md"),
    ("HSQL / H2 (JVM)", "docs/jvm_h2/index.md"),
]

OPTION_SECTION_RE = re.compile(r"^### `([^`]+)`\n(.*?)(?=^### `|\Z)", re.MULTILINE | re.DOTALL)
TYPE_RE = re.compile(r"Type: `([^`]+)`")
DEFAULT_RE = re.compile(r"Defaults to `([^`]+)`|Defaults to ([^\n.]+)")


def normalize_summary(section_text: str) -> str:
    lines = []
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("Type:") or line.startswith("Defaults to"):
            continue
        if line.startswith("===") or line.startswith("```") or line.startswith("{% include"):
            break
        if line.startswith("####"):
            break
        lines.append(line)
    return " ".join(lines).replace("|", "\\|")


def extract_gradle_options(repo_root: Path) -> list[dict[str, str]]:
    text = (repo_root / "docs" / "common" / "gradle.md").read_text()
    options: list[dict[str, str]] = []
    for name, section_text in OPTION_SECTION_RE.findall(text):
        type_match = TYPE_RE.search(section_text)
        default_match = DEFAULT_RE.search(section_text)
        default_value = ""
        if default_match:
            default_value = default_match.group(1) or default_match.group(2) or ""
        options.append(
            {
                "name": name,
                "type": type_match.group(1) if type_match else "",
                "default": default_value.strip(),
                "summary": normalize_summary(section_text),
            }
        )
    return options


def extract_dialects(repo_root: Path) -> list[dict[str, str]]:
    text = (repo_root / "docs" / "common" / "gradle.md").read_text()
    lines = text.splitlines()
    dialects: list[dict[str, str]] = []
    capture = False
    for line in lines:
        if "Available dialects:" in line:
            capture = True
            continue
        if capture:
            if not line.strip() and not dialects:
                continue
            if not line.strip():
                break
            match = re.match(r"\* ([^:]+): `([^`]+)`", line.strip())
            if match:
                family = match.group(1).strip()
                module = match.group(2).strip()
                dialects.append(
                    {
                        "family": family,
                        "module": module,
                    }
                )
    return dialects


def platform_row(repo_root: Path, label: str, relative_path: str) -> dict[str, str]:
    text = (repo_root / relative_path).read_text()
    frontmatter, _ = parse_frontmatter(text)
    rendered = render_includes(repo_root, relative_path.replace("docs/", ""))
    artifacts = collect_artifacts(rendered)
    constructors = constructors_in(rendered)

    dialect = str(frontmatter.get("dialect", ""))
    async_flag = "true" if frontmatter.get("async") else "false"
    server_flag = bool(frontmatter.get("server"))
    notes = []
    if async_flag == "true":
        notes.append("Requires async generated APIs.")
    if server_flag:
        notes.append("Uses the server JDBC setup pattern.")
    if "native_sqlite" in relative_path:
        notes.append("Native targets use the native driver path.")
    if "js_sqlite" in relative_path:
        notes.append("Browser-only web worker driver path.")

    return {
        "platform": label,
        "dialect": dialect or "see dialect matrix",
        "artifacts": ", ".join(artifacts),
        "constructors": ", ".join(constructors),
        "async": async_flag,
        "notes": " ".join(notes),
        "source": relative_path,
    }


def upgrade_rows(repo_root: Path) -> list[dict[str, str]]:
    text = (repo_root / "docs" / "upgrading-2.0.md").read_text()
    rows: list[dict[str, str]] = []
    pending_old: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("-") and "sqldelight" in line:
            pending_old = line[1:].strip()
            continue
        if line.startswith("+") and "sqldelight" in line and pending_old:
            rows.append({"old": pending_old, "new": line[1:].strip()})
            pending_old = None
    return rows


def build_matrix(repo_root: Path, skill_root: Path) -> tuple[Path, Path]:
    platform_rows = [platform_row(repo_root, label, relative) for label, relative in PLATFORM_DOCS]
    dialect_rows = extract_dialects(repo_root)
    option_rows = extract_gradle_options(repo_root)
    upgrade_rows_data = upgrade_rows(repo_root)

    lines = [
        "# Config Matrix (Generated)",
        "",
        "Generated from SQLDelight docs. Refresh this file with `scripts/build_config_matrix.py`.",
        "",
        "## Driver Matrix",
        "",
        "| Platform | Dialect module | Driver artifacts | Constructors | Async | Notes | Source docs |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in platform_rows:
        lines.append(
            "| {platform} | {dialect} | {artifacts} | {constructors} | {async} | {notes} | {source} |".format(
                **{key: value.replace("|", "\\|") for key, value in row.items()}
            )
        )

    lines.extend(
        [
            "",
            "## Dialect Modules",
            "",
            "| Family | Module |",
            "| --- | --- |",
        ]
    )
    for row in dialect_rows:
        lines.append(f"| {row['family']} | {row['module']} |")

    lines.extend(
        [
            "",
            "## Core Gradle Options",
            "",
            "| Option | Type | Default | Summary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in option_rows:
        lines.append(
            f"| {row['name']} | {row['type']} | {row['default']} | {row['summary']} |"
        )

    lines.extend(
        [
            "",
            "## Upgrade Coordinate Replacements",
            "",
            "| Old | New |",
            "| --- | --- |",
        ]
    )
    for row in upgrade_rows_data:
        lines.append(f"| {row['old']} | {row['new']} |")

    output_path = skill_root / "references" / "config-matrix.generated.md"
    output_path.write_text("\n".join(lines) + "\n")
    sync_path = write_sync_status(skill_root, repo_root)
    return output_path, sync_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the SQLDelight config matrix.")
    parser.add_argument("--repo-root", help="Path to a sqldelight repository checkout.")
    parser.add_argument("--skill-dir", help="Path to the sqldelight skill directory.")
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.repo_root)
    skill_root = skill_dir(args.skill_dir)
    output, sync_output = build_matrix(repo_root, skill_root)
    print(f"[OK] Wrote {output}")
    print(f"[OK] Wrote {sync_output}")


if __name__ == "__main__":
    main()
