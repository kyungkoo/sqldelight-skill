#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


LATEST_BASE_URL = "https://sqldelight.github.io/sqldelight/latest"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
INCLUDE_RE = re.compile(r"{%\s*include ['\"]([^'\"]+)['\"]\s*%}")
ARTIFACT_RE = re.compile(r"app\.cash\.sqldelight:([a-z0-9-]+)")
NPM_ARTIFACT_RE = re.compile(r"@cashapp/sqldelight-[a-z0-9-]+")

CONFIG_SYNC_SOURCES = (
    "mkdocs.yml",
    "docs/common/gradle.md",
    "docs/common/index_gradle_database.md",
    "docs/common/index_server.md",
    "docs/common/coroutines.md",
    "docs/common/coroutines-multiplatform.md",
    "docs/common/migrations.md",
    "docs/common/migrations_server.md",
    "docs/common/custom_column_types.md",
    "docs/common/types_sqlite.md",
    "docs/common/types_server_migrations.md",
    "docs/upgrading-2.0.md",
    "docs/android_sqlite/index.md",
    "docs/multiplatform_sqlite/index.md",
    "docs/native_sqlite/index.md",
    "docs/jvm_sqlite/index.md",
    "docs/js_sqlite/index.md",
    "docs/jvm_mysql/index.md",
    "docs/jvm_postgresql/index.md",
    "docs/jvm_h2/index.md",
)

DOC_CATALOG_SYNC_SOURCES = ("mkdocs.yml",)


def require_yaml() -> None:
    if yaml is None:  # pragma: no cover
        raise SystemExit("PyYAML is required for this script. Install it or run in the Codex environment.")


def skill_dir(default: str | None = None) -> Path:
    if default:
        return Path(default).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def resolve_repo_root(repo_root_arg: str | None) -> Path:
    candidates = []
    if repo_root_arg:
        candidates.append(Path(repo_root_arg).expanduser())
    env_root = os.environ.get("SQLDELIGHT_REPO_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.append(Path.cwd())

    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "mkdocs.yml").exists() and (resolved / "docs").is_dir():
            return resolved

    raise SystemExit("Could not resolve a SQLDelight repo root. Pass --repo-root /path/to/sqldelight.")


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    frontmatter_text = match.group(1)
    body = text[match.end() :]

    if yaml is not None:
        data = yaml.safe_load(frontmatter_text) or {}
        if isinstance(data, dict):
            return data, body

    data: dict[str, object] = {}
    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value.lower() == "true":
            data[key] = True
        elif value.lower() == "false":
            data[key] = False
        else:
            data[key] = value
    return data, body


def read_markdown(path: Path) -> tuple[dict[str, object], str]:
    return parse_frontmatter(path.read_text())


def render_includes(repo_root: Path, doc_path: str, seen: set[str] | None = None) -> str:
    seen = seen or set()
    if doc_path in seen:
        raise SystemExit(f"Include cycle detected while rendering {doc_path}")
    seen.add(doc_path)

    full_path = repo_root / "docs" / doc_path
    if not full_path.exists():
        raise SystemExit(f"Missing documentation source: {full_path}")

    _, body = read_markdown(full_path)

    def replace(match: re.Match[str]) -> str:
        include_path = match.group(1)
        return render_includes(repo_root, include_path, seen.copy())

    return INCLUDE_RE.sub(replace, body)


def official_url(doc_path: str) -> str:
    normalized = doc_path.lstrip("/")
    if normalized.endswith("index.md"):
        suffix = normalized[: -len("index.md")]
    elif normalized.endswith(".md"):
        suffix = normalized[: -len(".md")] + "/"
    else:
        suffix = normalized
    suffix = suffix.lstrip("/")
    if not suffix:
        return f"{LATEST_BASE_URL}/"
    return f"{LATEST_BASE_URL}/{suffix}"


def load_mkdocs(repo_root: Path) -> dict[str, object]:
    text = (repo_root / "mkdocs.yml").read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    return {"nav": parse_nav_block(text)}


def parse_nav_block(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    in_nav = False
    rows: list[dict[str, str]] = []
    stack: list[tuple[int, str]] = []

    for line in lines:
        if not in_nav:
            if line.strip() == "nav:":
                in_nav = True
            continue

        if in_nav and line and not line.startswith(" "):
            break
        if not line.strip():
            continue

        match = re.match(r"^( +)-\s+['\"]([^'\"]+)['\"]:(?:\s*(.+))?$", line)
        if not match:
            continue

        indent = len(match.group(1))
        title = match.group(2)
        value = (match.group(3) or "").strip()

        while stack and stack[-1][0] >= indent:
            stack.pop()

        if value:
            section = stack[0][1] if stack else title
            category = " > ".join(entry[1] for entry in stack[1:])
            rows.append(
                {
                    "section": section,
                    "category": category,
                    "title": title,
                    "path": value,
                }
            )
        else:
            stack.append((indent, title))
    return rows


def flatten_nav(nav_items: list[object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def visit(items: list[object], trail: list[str]) -> None:
        for item in items:
            if isinstance(item, dict):
                for title, value in item.items():
                    if isinstance(value, list):
                        visit(value, trail + [title])
                    elif isinstance(value, str):
                        section = trail[0] if trail else title
                        category = " > ".join(trail[1:]) if len(trail) > 1 else ""
                        rows.append(
                            {
                                "section": section,
                                "category": category,
                                "title": title,
                                "path": value,
                            }
                        )
                    elif isinstance(value, dict):
                        visit([value], trail + [title])

    visit(nav_items, [])
    return rows


def slug_tokens(*parts: str) -> list[str]:
    tokens: list[str] = []
    for part in parts:
        for token in re.split(r"[^a-z0-9]+", part.lower()):
            if token:
                tokens.append(token)
    return tokens


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def topic_tags(row: dict[str, str]) -> list[str]:
    tokens = slug_tokens(row["section"], row["category"], row["title"], row["path"])
    tags: list[str] = []

    if "android" in tokens:
        tags.append("android")
    if "multiplatform" in tokens:
        tags.append("multiplatform")
    if "native" in tokens:
        tags.append("native")
    if "jvm" in tokens:
        tags.append("jvm")
    if "js" in tokens or "javascript" in tokens:
        tags.append("js")
    if "sqlite" in tokens:
        tags.append("sqlite")
    if "mysql" in tokens:
        tags.append("mysql")
    if "postgresql" in tokens or "postgres" in tokens:
        tags.append("postgresql")
    if "hsql" in tokens or "h2" in tokens:
        tags.append("hsql")
    if "gradle" in tokens:
        tags.append("gradle")
    if "migration" in tokens or "migrations" in tokens:
        tags.append("migrations")
    if "coroutines" in tokens:
        tags.append("coroutines")
    if "paging" in tokens:
        tags.append("paging")
    if "plugin" in tokens:
        tags.append("ide-plugin")
    if "types" in tokens or "type" in tokens:
        tags.append("types")
    if "transactions" in tokens or "transaction" in tokens:
        tags.append("transactions")
    if "query" in tokens or "queries" in tokens or "arguments" in tokens:
        tags.append("queries")
    if "upgrade" in tokens or "upgrading" in tokens:
        tags.append("upgrade")
    if "api" in tokens or row["path"].endswith(".html"):
        tags.append("api")
    if "getting" in tokens and "started" in tokens:
        tags.append("setup")
    return unique(tags)


def intent_for_row(row: dict[str, str]) -> str:
    title = row["title"].lower()
    section = row["section"]

    if title == "overview":
        return "Start at the top-level SQLDelight overview."
    if "getting started" in title:
        return f"Set up {section}."
    if "gradle" in title:
        return "Find Gradle plugin and database DSL options."
    if "migration" in title:
        return "Plan, verify, or output schema migrations."
    if "coroutines" in title:
        return "Integrate coroutines or Flow support."
    if "paging" in title:
        return "Integrate query results with Paging."
    if "plugin" in title:
        return "Use the IntelliJ or Android Studio plugin."
    if "types" in title:
        return "Map SQL types, adapters, and exposed Kotlin types."
    if "transactions" in title:
        return "Use transactions, rollback, and callbacks."
    if "arguments" in title or "query" in title:
        return "Define and call generated query APIs."
    if "resources" in title:
        return "Open external examples and ecosystem links."
    if row["path"].endswith(".html"):
        return "Inspect generated 2.x API docs."
    return f"Open the {row['title']} page for {section}."


def collect_artifacts(text: str) -> list[str]:
    artifacts = [match.group(1) for match in ARTIFACT_RE.finditer(text)]
    artifacts.extend(match.group(0) for match in NPM_ARTIFACT_RE.finditer(text))
    return unique(artifacts)


def constructors_in(text: str) -> list[str]:
    names = re.findall(r"\b([A-Z][A-Za-z0-9]+Driver)\(", text)
    return unique(names)


def git_head(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unavailable"


def fingerprint(repo_root: Path, relative_paths: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(unique(relative_paths)):
        path = repo_root / relative
        digest.update(relative.encode("utf-8"))
        if path.exists():
            digest.update(path.read_bytes())
        else:
            digest.update(b"<missing>")
    return digest.hexdigest()


def generated_reference_paths(skill_root: Path) -> list[str]:
    return sorted(
        str(path.relative_to(skill_root))
        for path in (skill_root / "references").glob("*.generated.md")
    )


def write_sync_status(skill_root: Path, repo_root: Path) -> Path:
    generated_files = generated_reference_paths(skill_root)
    generated_rel = "references/sync-status.generated.md"
    if generated_rel not in generated_files:
        generated_files.append(generated_rel)
        generated_files.sort()

    repo_relative_sources = list(CONFIG_SYNC_SOURCES)
    text = "\n".join(
        [
            "# Sync Status (Generated)",
            "",
            f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
            f"- Repo root: `{repo_root}`",
            f"- Git HEAD: `{git_head(repo_root)}`",
            f"- Source fingerprint: `{fingerprint(repo_root, repo_relative_sources)}`",
            f"- Source files tracked: `{len(repo_relative_sources)}`",
            "",
            "## Generated Files",
            *[f"- `{path}`" for path in generated_files],
            "",
            "## Fingerprint Inputs",
            *[f"- `{path}`" for path in repo_relative_sources],
            "",
            "This file is regenerated by `build_config_matrix.py` after generated references are refreshed.",
            "",
        ]
    )
    output_path = skill_root / generated_rel
    output_path.write_text(text)
    return output_path


def source_fingerprint_from_sync(sync_text: str) -> str | None:
    match = re.search(r"- Source fingerprint: `([0-9a-f]+)`", sync_text)
    if match:
        return match.group(1)
    return None


def listed_generated_files(sync_text: str) -> list[str]:
    if "## Generated Files" not in sync_text:
        return []
    after = sync_text.split("## Generated Files", 1)[1]
    before = after.split("## Fingerprint Inputs", 1)[0]
    return re.findall(r"- `([^`]+)`", before)
