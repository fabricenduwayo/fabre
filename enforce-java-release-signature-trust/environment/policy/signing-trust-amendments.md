# Artifact signing trust policy - Amendments

These amendments override `/app/policy/signing-trust-policy.md` wherever they
conflict.

## A-2026-01 - evidence is a chain

`artifact_evidence` may hold several rows per artifact. At most one is operative,
and only the operative row's `sha256_digest`, `signer_key_id`, `signed_at`, and
`tsa_id` bear on trust. Non-operative rows have no standing of any kind.

## A-2026-02 - operative selection

The operative row is the row with the greatest `recorded_at` among rows that are
neither void under A-2026-03 nor discarded under A-2026-05, and whose `status` is
exactly `attested`. Break a tie by lexicographically greatest `evidence_id`. Rows
with status `provisional` or `withdrawn` are never operative whatever their
`recorded_at`.

## A-2026-03 - supersession voiding

Among an artifact's amendments that are not discarded under A-2026-05, the one with
the greatest `recorded_at` voids the row it references; break a tie by
lexicographically greatest `evidence_id`. Then void any row whose `evidence_id`
equals a voided row's `supersedes_evidence_id`, repeating until the void set stops
growing. This is settled before A-2026-02 selects.

## A-2026-04 - a superseding row voids regardless of its own standing

Voiding under A-2026-03 is independent of the referring row's `status`, though not
of the authority A-2026-05 requires. A `withdrawn` or `provisional` row voids what
it supersedes even though A-2026-02 will never let it become operative.

An artifact whose every row is void, discarded, or not `attested` has no operative
evidence and is recorded `quarantine` with reason_code `no_operative_evidence`. An
artifact with no `artifact_evidence` rows at all is instead recorded `quarantine`
with reason_code `missing_evidence`. Both are `quarantine`; only the reason_code
differs.

## A-2026-05 - amendment authority

A row with a non-null `supersedes_evidence_id` is an amendment, and
`amendment_key_id` is the key that authorised it. The amendment is discarded unless
that key was live, as A-2026-06 defines live, as of the amendment row's own
`recorded_at`. A null `amendment_key_id` is not live.

A discarded amendment is not operative under A-2026-02 and voids nothing under
A-2026-03. It loses its voiding power, not only its candidacy, so the row it names
stands. A discarded amendment is inert in the A-2026-03 cascade: its own
`supersedes_evidence_id` is never followed, even when the discarded row is itself
voided. Amendment authority is settled before A-2026-03 computes the void set.

## A-2026-06 - live

A key is live as of an instant T when it is not revoked as of T under A-2026-07 and
A-2026-08, and T falls within its half-open `[not_before, not_after)` window. The
countersignature rule in A-2026-10 has no bearing on whether a key is live.

## A-2026-07 - key state is replayed, not read

There is no revocation column. Replay `key_lifecycle_events` per `key_id` ordered by
effective instant, breaking a tie by lexicographic `event_id`. A key is revoked as
of an instant T when the latest event whose effective instant is at or before T is a
`revoke`.

## A-2026-08 - effective instant

A `revoke` whose `reason` is `key_compromise` takes effect at its `effective_from`,
or at its `occurred_at` when `effective_from` is null. A `revoke` with any other
reason takes effect at its `occurred_at`, and its `effective_from` is disregarded.
An `activate` takes effect at its `occurred_at`.

## A-2026-09 - trust is evaluated at signing time

The signer's standing is assessed as of the operative row's `signed_at`, not at the
instant the worker runs. A signature made while its key was revoked as of that
`signed_at` is `denied` with reason_code `revoked_signer`. This is settled before
A-2026-10.

## A-2026-10 - validity window and countersignature

A `signed_at` outside the signing key's half-open `[not_before, not_after)` window
is `denied` with reason_code `expired_key_signature`, unless the operative row names
a `tsa_id` whose own half-open `[valid_from, valid_until)` window covers that
`signed_at`. A countersignature extends a signature past the end of its key's
validity. It confers nothing against A-2026-09.

## A-2026-11 - channel exposure

A `key_compromise` revocation exposes every release channel that contains an
artifact whose operative evidence names the compromised key as `signer_key_id`. The
channel is exposed from that revocation's effective instant under A-2026-08, and
where more than one compromise reaches a channel the earliest such instant governs.
Artifacts count towards this whether or not they appear in `pending_attestations`,
and whatever verdict they themselves received.

Exposure is arbitrated after every artifact already has a verdict. It downgrades a
`trusted` verdict to `quarantine` with reason_code `channel_exposure` and does
nothing else. It never changes a `denied` verdict, never changes a verdict that is
already `quarantine`, and never promotes anything.

An artifact in an exposed channel keeps its `trusted` verdict when its operative row
names a `tsa_id` whose window covers that row's `signed_at` and that `signed_at` is
strictly earlier than the instant the channel became exposed.
