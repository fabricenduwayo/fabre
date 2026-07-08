# reconcile-model-release

A command-line step that decides whether a candidate model release may be promoted.
When complete, it loads the promotion policy, reads release metadata from the embedded
H2 store, consults the model registry, and writes a `build/release-decision.json`
manifest describing the outcome.

## Build

```sh
mvn package
```

This produces a runnable fat jar at `target/reconcile-model-release-0.1.0.jar`.

## Run

```sh
java -jar target/reconcile-model-release-0.1.0.jar
```

The reconciliation logic is still being built out, so the step currently prints a
placeholder notice and exits successfully.

## Layout

- `src/main/java/com/example/reconcile/App.java` — CLI entry point.
- `pom.xml` — build definition and pinned dependencies (H2, Jackson, json-schema-validator).
