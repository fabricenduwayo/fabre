# Artifact signing trust policy

This policy governs how a release artifact earns trust. Trust follows the signing
evidence: an artifact is trusted only when its detached signature verifies against
the canonical digest under a signing key that was fit to sign it. Registry
metadata is convenience data, not a basis for trust.

The worker at `/app/attest-worker` processes every row in `pending_attestations` in
`enqueued_at` order and writes one row per artifact into `attestation_reports`. The
queue is an input, not a work list to consume: rows stay in `pending_attestations`
after a run, and the worker never deletes or updates them.

The amendments in `/app/policy/signing-trust-amendments.md` override this body
wherever they disagree.

## Canonical evidence

`artifact_evidence` in H2 is authoritative for `sha256_digest`, `signer_key_id`,
`signed_at`, and the countersignature. Registry JSON from the artifact-metadata API
is not. An artifact has at most one operative evidence row and only that row bears
on trust; A-2026-01 through A-2026-05 settle which row it is.

Signing keys are described by `signing_keys` and their history by
`key_lifecycle_events`. There is no revocation column anywhere; key state is
derived, and it is a fact about a key at an instant rather than a fact about an
artifact. A-2026-06 through A-2026-10 settle it.

`GET http://localhost:8080/artifacts/{id}` returns registry metadata including
`registry_digest` and `detached_signature`. The registry digest may lag H2; never
use it as the verify digest.

## Signature verification

After a successful artifact lookup, call `POST http://localhost:8080/verify` with
JSON:

```json
{"artifact_id":"<id>","digest":"<operative sha256_digest from H2>","detached_signature":"<from GET>"}
```

A `GET` success does not skip verify. Detached-signature validation happens only on
`POST /verify`.

Everything an artifact can fail on before the registry is contacted is settled
without contacting it. `missing_evidence`, `no_operative_evidence`,
`revoked_signer`, and `expired_key_signature` are all reached with no API call.

## API outcomes

A registry lookup that reports the artifact unknown denies it as `unknown_artifact`.
A lookup that reports the registry degraded quarantines it as `registry_degraded`,
and any other unsuccessful lookup quarantines it as `registry_error`.

Verification that succeeds trusts the artifact as `verified`. Verification that
rejects the detached signature denies it as `bad_signature`, and verification that
rejects the submitted digest against the canonical digest it holds denies it as
`digest_mismatch`. Verification that does not know the artifact denies it as
`unknown_artifact`. Verification that reports itself degraded quarantines it as
`verify_degraded`, and any other unsuccessful verification quarantines it as
`verify_error`.

The API names the condition it found in the `error` field of its response body.

## Reason codes

`verified` - the operative detached signature verified against the operative
canonical digest under a key that was fit to sign it.
`revoked_signer` - the operative row's signing key was revoked as of that row's
`signed_at`.
`expired_key_signature` - the operative row's `signed_at` fell outside its signing
key's validity window and no countersignature covered it.
`channel_exposure` - the artifact's release channel was exposed by a key compromise
and the artifact is not exempt under A-2026-11.
`missing_evidence` - the artifact has no `artifact_evidence` row at all.
`no_operative_evidence` - the artifact has `artifact_evidence` rows but none of them
is operative.
`bad_signature`, `digest_mismatch`, `unknown_artifact`, `registry_degraded`,
`registry_error`, `verify_degraded`, `verify_error` - as described under API
outcomes.

`verified` is the only `trusted` reason code. Codes naming a transient condition of
a service, or an absence of evidence to decide on, are recorded as `quarantine`;
codes naming a defect in the evidence or the signing key are recorded as `denied`.

`checked_at` is the worker timestamp when the verdict is recorded.
