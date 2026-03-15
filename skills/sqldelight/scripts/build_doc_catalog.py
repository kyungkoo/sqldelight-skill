#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from _common import flatten_nav, intent_for_row, load_mkdocs, official_url, resolve_repo_root, skill_dir, topic_tags


def local_source(path: str) -> str:
    if path.endswith(".md"):
        return f"docs/{path}"
    return f"generated-site:{path}"


def build_catalog(repo_root: Path, skill_root: Path) -> Path:
    mkdocs = load_mkdocs(repo_root)
    nav = mkdocs.get("nav", [])
    rows = nav if nav and isinstance(nav[0], dict) and {"section", "title", "path"}.issubset(nav[0].keys()) else flatten_nav(nav)

    lines = [
        "# Doc Catalog (Generated)",
        "",
        "Generated from `mkdocs.yml`. Refresh this file with `scripts/build_doc_catalog.py`.",
        "",
        "| Section | Page | Intent | Official latest URL | Local source path | Topic tags |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        tags = ", ".join(topic_tags(row))
        lines.append(
            "| {section} | {page} | {intent} | {url} | {source} | {tags} |".format(
                section=row["section"],
                page=row["title"],
                intent=intent_for_row(row),
                url=official_url(row["path"]),
                source=local_source(row["path"]),
                tags=tags,
            )
        )

    output_path = skill_root / "references" / "doc-catalog.generated.md"
    output_path.write_text("\n".join(lines) + "\n")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the SQLDelight documentation catalog.")
    parser.add_argument("--repo-root", help="Path to a sqldelight repository checkout.")
    parser.add_argument("--skill-dir", help="Path to the sqldelight skill directory.")
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.repo_root)
    skill_root = skill_dir(args.skill_dir)
    output = build_catalog(repo_root, skill_root)
    print(f"[OK] Wrote {output}")


if __name__ == "__main__":
    main()
