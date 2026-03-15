# SQLDelight Checklists

Use these lists to make offline answers useful and to avoid skipping the setup steps that most often cause bad guidance.

## Initial Adoption

- Confirm the target runtime and dialect before naming an artifact.
- Confirm whether the project is Android-only, multiplatform, browser JS, or JVM server.
- Confirm whether the schema should start from `.sq` files or existing `.sqm` migrations.
- Check that the Gradle plugin ID matches the current SQLDelight group.
- Check that the selected driver artifact matches the runtime, not just the SQL dialect.
- Check that the generated database package and source directories are explicit when the project layout is non-default.

## Fresh Schema vs Migration Schema

- If the database already exists in production, prefer migration-backed schema.
- If the project is greenfield, prefer `.sq` schema files unless another service already owns migrations.
- If using `deriveSchemaFromMigrations`, check every dependent module that consumes the schema path.
- If using migrations as the source of truth, check whether another service also needs valid SQL output files.
- Do not mix both strategies casually in the same explanation. State which one is the source of truth.

## Migration Verification

- Check whether `schemaOutputDirectory` is configured before recommending migration verification tasks.
- Check whether the project stores only the minimal `.db` baselines it actually needs.
- Check whether `.sqm` files live in the same SQLDelight source set as related queries.
- If the project needs SQL migrations for Flyway or another service, check `migrationOutputDirectory` and output format guidance.
- If code migrations are involved, verify whether `AfterVersion` callbacks are part of the plan.

## Async and Coroutines

- Check whether the selected driver is asynchronous or only the consumer API is reactive.
- For browser JS, confirm that `generateAsync` is enabled.
- If generated async APIs are in use, avoid recommending blocking `executeAs*()` calls where `awaitAs*()` is required.
- For coroutines, verify the correct extensions artifact and remember that dispatcher arguments are required in 2.x coroutine mappings.
- In multiplatform answers, call out where the async requirement affects only some targets.

## Custom Types and Adapters

- If a column uses `AS SomeType`, check whether a `ColumnAdapter` must be provided to the generated database.
- For primitive wrapper mappings, check whether `primitive-adapters` is the simpler solution.
- For enums, prefer the runtime enum adapter path before suggesting custom serialization.
- If migrations are the source of truth, verify whether custom types appear in `.sqm` files and whether downstream SQL consumers need plain SQL output.
- If the user mentions `LOCK` or value types, confirm whether generated value wrappers change update semantics.

## Upgrade to 2.x

- Check the plugin ID and Maven group first.
- Check the Java build requirement before blaming Gradle configuration.
- Check renamed DSL properties such as `srcDirs`.
- Check whether callback migrations still refer to removed APIs like `AfterVersionWithDriver`.
- Check whether coroutine examples pass a dispatcher explicitly.
- Check whether JS or mixed async projects now rely on `QueryResult` and async-compatible generated schema types.
