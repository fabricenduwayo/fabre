The release attestation worker at `/app/attest-worker` should drain pending rows from `jdbc:h2:file:/app/attestation-db/attestation`, call the bundled artifact-metadata API on port 8080 (`bash /app/start-api.sh` if needed), and write one row per artifact into `attestation_reports` with verdict `trusted`, `denied`, or `quarantine`.

Follow `/app/policy/attestation-policy.md`. Canonical digest and signer revocation come from `artifact_evidence` in H2, not from registry JSON. `GET /artifacts/{id}` supplies the detached signature; you still must `POST /verify` with the H2 digest. Map API status codes per the policy table.

Build with `/app/attest-worker/build.sh` and run `com.snorkel.attest.Main`. Optional JDBC URL argument defaults to the path above; pointing it at another compatible store must yield that store's reports.
