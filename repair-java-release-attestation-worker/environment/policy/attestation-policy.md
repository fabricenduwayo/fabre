# Release attestation policy

The worker at `/app/attest-worker` drains `pending_attestations` in `enqueued_at` order and writes one row per artifact into `attestation_reports`.

## Canonical evidence

`artifact_evidence` in H2 is authoritative for `sha256_digest`, `signer_key_id`, and `revoked`. Registry JSON from the artifact-metadata API is not.

`GET http://localhost:8080/artifacts/{id}` returns registry metadata including `registry_digest` and `detached_signature`. The registry digest may lag H2; never use it as the verify digest.

## Verify step

After a successful artifact lookup, call `POST http://localhost:8080/verify` with JSON:

```json
{"artifact_id":"<id>","digest":"<sha256_digest from H2>","detached_signature":"<from GET>"}
```

A `GET` success does not skip verify. Detached-signature validation happens only on `POST /verify`.

## HTTP mapping

| Step | Status | Verdict | reason_code |
|------|--------|---------|-------------|
| H2 `revoked = true` | (skip API) | denied | revoked_signer |
| GET | 404 | denied | unknown_artifact |
| GET | 503 | quarantine | registry_degraded |
| GET | other non-200 | quarantine | registry_error |
| POST | 200 and signer not revoked | trusted | verified |
| POST | 400 | denied | bad_signature |
| POST | 404 | denied | unknown_artifact |
| POST | 409 | denied | digest_mismatch |
| POST | 503 | quarantine | verify_degraded |
| POST | other non-200 | quarantine | verify_error |

An artifact with no `artifact_evidence` row is recorded as `quarantine` with reason_code `missing_evidence`.

`checked_at` is the worker timestamp when the verdict is recorded.
