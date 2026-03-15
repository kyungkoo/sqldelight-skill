---
description: SQLDelight assistant - setup, driver selection, schema strategy, migration planning, and Gradle config generation for Kotlin projects
argument-hint: "[setup|migration|driver|config|schema|troubleshoot] [platform/question]"
allowed-tools: Bash, Glob, Grep, Read, Task
---

## Phase 1: Auto-scan project signals

Gather project signals automatically before doing anything else:

`!find . -name "build.gradle*" -o -name "settings.gradle*" -o -name "libs.versions.toml" | head -20`

`!grep -r "sqldelight\|SqlDelight\|android-driver\|native-driver\|sqlite-driver\|web-worker" --include="*.gradle" --include="*.kts" --include="*.toml" -l 2>/dev/null | head -10`

`!find . -name "*.sq" -o -name "*.sqm" 2>/dev/null | head -20`

> If no project files are found, this command still works for general SQLDelight questions — just skip to Phase 2 with the user's arguments as the sole context.

## Phase 2: Classify request mode

Parse `$ARGUMENTS` to determine the operating mode:

| Keyword in $ARGUMENTS | Mode |
|------------------------|------|
| `setup` | Fresh project setup |
| `migration` | Migration strategy and execution |
| `driver` | Driver and dialect selection only |
| `config` | Gradle DSL generation only |
| `schema` | Schema design strategy |
| `troubleshoot` or `troubleshooting` | Diagnose problems |
| _(none of the above)_ | Auto-detect from project scan context |

## Phase 3: Dispatch agents based on mode

Use the Task tool to launch agents in parallel or sequentially depending on the mode.
Pass `$ARGUMENTS` as context to each agent so they can tailor their output.

| Mode | Agent dispatch strategy |
|------|------------------------|
| `setup` | Launch `project-analyzer`, `driver-selector`, and `config-generator` in parallel |
| `migration` | Launch `project-analyzer` and `schema-advisor` in parallel |
| `driver` | Launch `project-analyzer` and `driver-selector` in parallel |
| `config` | Launch `project-analyzer` first (sequential), then `config-generator` with its output |
| `schema` | Launch `project-analyzer` and `schema-advisor` in parallel |
| `troubleshoot` | Launch `project-analyzer` and `schema-advisor` in parallel |
| _(auto-detect)_ | Launch `project-analyzer` first, then dispatch appropriate agents based on findings |

## Phase 4: Synthesize and present results

Combine all agent outputs into a single, structured answer using this format:

### 1. Detected Config
Summarize what `project-analyzer` found: platform, Gradle DSL style, SQLDelight version, existing drivers, and any existing `sqldelight {}` block.

### 2. Recommendation
State clearly what to do based on the detected config and the user's request mode.

### 3. Why
Explain the reasoning tailored to their specific platform, existing setup, and the mode they requested.

### 4. Exact Configuration
Provide copy-paste ready Gradle DSL (Kotlin DSL by default, Groovy DSL if detected). Include:
- Plugin declaration
- Driver dependency declarations
- Complete `sqldelight {}` block with database name, package name, and dialect

### 5. Anti-patterns to avoid
List common mistakes specific to their platform and setup, such as:
- Using the wrong driver for a target
- Missing `generateDatabaseInterface = true` for KMP
- Placing `.sq` files in the wrong source set
- Forgetting to configure the dialect

### 6. Official docs
Link to the relevant SQLDelight documentation:
- Getting started: https://cashapp.github.io/sqldelight/
- Android: https://cashapp.github.io/sqldelight/android_sqlite/
- KMP: https://cashapp.github.io/sqldelight/multiplatform_sqlite/
- JVM: https://cashapp.github.io/sqldelight/jvm_sqlite/
- JS: https://cashapp.github.io/sqldelight/js_sqlite/
- Migrations: https://cashapp.github.io/sqldelight/migrations/
