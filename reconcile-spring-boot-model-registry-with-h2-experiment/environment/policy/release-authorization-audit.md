# Release authorization audit contract

The promotion gate at `/app/reconcile-model-release` must enforce the governance bundle under `/app/policy/`. The reconciler is a fail-closed authorization decision over registry candidates: it reads the candidate set from the registry API, treats H2 experiment evidence as canonical for metrics, calibration, lineage, and waiver state, and writes `/app/build/release-decision.json`.

Waiver grants are version-scoped authorization exceptions. Only an active grant that matches a specific raw gate failure may suppress that failure; reporting a grant under `applied_waivers` does not imply promotion when another unsuppressed failure remains.

The bundled schema at `/app/schemas/release-decision.schema.json` defines the authorized decision shape. Do not modify policy sources or registry service data to force agreement.
