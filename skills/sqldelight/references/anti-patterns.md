# SQLDelight Anti-Patterns

Use this file to prevent bad recommendations before they reach the user.

## Mixing Schema Strategies Without Saying Which One Wins

Problem:
- Recommending `.sq` schema files and migration-derived schema in the same setup without naming the source of truth.

Fix:
- State the source of truth explicitly.
- If the project already has production schema history, recommend migrations first.

## Recommending the Wrong Driver for the Runtime

Problem:
- Picking a driver from the SQL dialect alone instead of the runtime target.

Fix:
- Start from runtime first, then dialect.
- Verify the driver row in `config-matrix.generated.md`.

## Treating JS as Synchronous

Problem:
- Suggesting the pre-2.0 sync JS path or omitting `generateAsync`.

Fix:
- Treat browser JS as the async web worker path.
- Verify async generation and the web worker setup docs.

## Forgetting `ColumnAdapter`

Problem:
- Suggesting `AS SomeType` in schema files without wiring the adapter into the generated database constructor.

Fix:
- Mention both sides together: schema declaration and database adapter injection.
- Suggest `primitive-adapters` when it matches the needed conversion.

## Recommending Migration Verification Without Schema Outputs

Problem:
- Telling users to rely on verification tasks without `schemaOutputDirectory` or baseline `.db` files.

Fix:
- Check the schema output configuration first.
- Only recommend verification tasks when the stored schema outputs exist.

## Missing 2.x Upgrade Breaks

Problem:
- Keeping old `com.squareup.sqldelight` coordinates, old callback APIs, or old coroutine examples.

Fix:
- Check plugin ID, group, callback type, and dispatcher-aware coroutine examples before answering.

## Ignoring Native Linking Context

Problem:
- Assuming Kotlin/Native linking works without discussing `linkSqlite` or linker settings when the framework shape matters.

Fix:
- Mention the native linking option and point to the Gradle page when iOS or native frameworks are part of the question.

## Copying Blocking Query Examples Into Async Contexts

Problem:
- Reusing `executeAsList()` or similar blocking snippets when the generated APIs or drivers are async-oriented.

Fix:
- Match the example style to the runtime model.
- In async contexts, call out the `awaitAs*()` family and the `QueryResult` changes where relevant.
