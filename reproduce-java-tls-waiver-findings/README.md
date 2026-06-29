# reproduce-java-tls-waiver-findings

A three-milestone task that reconstructs the mid-year 2026 Mariner transport-security
waiver review from source. The decisive facts are deliberately split across three
places that have to be reconciled: a long narrative report, a binary H2 inventory
database reached over JDBC, and a YAML/TOML policy set. The deliverable is a small
Java command pipeline that emits schema-valid JSON evidence reproducing the review's
final allow / deny / rotate dispositions.

The agent works the same container across all three milestones (cumulative state):

- **Milestone 1 — Decode Waiver Narrative.** Read `/app/reports/mariner-tls-waiver-review.md`
  (~70k tokens) and decode the per-service waiver register into `/app/out/waivers.json`.
  Waivers are granted in Appendix B and some are later rescinded, so only the net state
  at the review date counts.
- **Milestone 2 — Join Probe Evidence.** Query the H2 database for each service's
  environment, certificate of record, and *latest* captured probe, join in the decoded
  waiver, and write `/app/out/evidence.json`.
- **Milestone 3 — Validate Config Schemas.** Validate `policy.yaml`/`crypto.toml` against
  their JSON Schemas, then apply the report's normative adjudication precedence to emit
  `/app/out/findings.json`.

## Why it is not keyword search

The report never states a per-service verdict, and DB-only facts (issuer, key size,
observed fingerprint, probe outcomes) are not transcribed into the narrative — they must
be queried. Conversely, the adjudication precedence (e.g. a fingerprint mismatch denies
even under an active waiver; an out-of-scope waiver does not excuse a prod mTLS gap) lives
only in the report, not the database. Reproducing the findings requires holding all three
sources together.

## Layout

- `environment/reports/mariner-tls-waiver-review.md` — long-context policy + dossiers + appendices
- `environment/config/{policy.yaml,crypto.toml}` — operative policy and crypto parameters
- `environment/schema/*.json` — JSON Schemas for both inputs and the three outputs
- `environment/data/` — H2 store, seeded from `seed.sql` at build time (the SQL is then deleted)
- `environment/lib/` — vendored offline jars (H2, Jackson core/databind/yaml/toml, networknt validator)
- `steps/milestone_{1,2,3}/` — per-milestone `instruction.md`, oracle `solution/`, hidden `tests/`
- `tools/reference.py` — single source of truth for the dataset and the decision logic
- `tools/gen_dataset.py`, `tools/gen_report.py` — regenerate the seed/config/schemas/report and the hidden `expected_*.json`

The ground-truth registers/evidence/findings live only in the hidden tests; the agent must
derive them.

## Difficulty

Difficulty is measured from accuracy over 5 runs on the two frontier models (Opus 4.8 and
GPT-5.5) and recorded in `task.toml`. Output field names and allowed values are fixed by the
schemas under `/app/schema/`; the per-service dispositions must be derived.

## Base image

Final runtime uses the canonical Terminal-Bench Python base
(`python:3.13-slim-bookworm`, digest-pinned) with OpenJDK 17 added for the Java pipeline and
H2 seeding. All Java dependencies are vendored under `environment/lib/`, so the build and the
run are hermetic and work with `allow_internet = false`.
