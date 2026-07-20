I have everything I need. The diagnosis checks out: the delta is a 43-line table transcription, `signer_key_id` is dead even in the oracle, and the DB is built at image build (no committed `.mv.db`, so the ALTER-vs-CREATE concern is moot).

---

# 1. CHOSEN DESIGN

**"Operative signing evidence: amendment chains, key-lifecycle authority, and artifact-derived channel exposure"**

Design #1 (highest total, **zero fatals**) as the base, plus **one mechanic lifted from design #3: channel exposure**, re-specified so exposure scope is *derived from artifacts* rather than read off a `signing_keys.channel_id` column.

Why this base: designs #2, #3, #4 each carry a judge-declared fatal (missing `verified` code; undefined valid-`retire` semantics; run-count-dependent grading via stateful API counters). #4's fatal is disqualifying here specifically because `ApiServer` is stateless today and `start-api.sh` short-circuits on a healthy process, so counter-based degradation cannot be reset by the agent. Design #1 needs no API state at all.

Why add channel exposure: it is the *only* judge criticism of design #1 that touches difficulty rather than cost. Judge 1 fix #3 asked for "one cross-artifact dependency that is not a shared key." Making exposure scope artifact-derived does exactly that: `art-omega` is signed by a clean key that is never revoked, yet its verdict is decided by *another artifact's* operative signer. It also forces a two-phase worker (resolve every operative row → compute exposure → evaluate), so the loop body cannot be written while thinking about one artifact. Cost is low because it reuses machinery A-2026-08 and A-2026-10 already build.

**Judge fixes folded in:**

| Fix | Source | Action |
|---|---|---|
| Trim 15 → ~11 artifacts, no legacy-only padding | J1.1 | 14 artifacts; 12 isolate a derivation mechanic, 2 cover stated API outcomes |
| Add a cross-artifact dependency that is not a shared key | J1.3 | Artifact-derived channel exposure |
| Pin every reason_code as a backticked literal in prose | J1.4 | Glossary in policy body, all 13 codes |
| `ENV TZ=UTC` | J1.5, J2.6, J3.4 | Dockerfile, plus zone-free `LocalDateTime` on both sides |
| Verifier asserts registry fixtures before agent output | J1.6, J2.2, J4.2 | `test_registry_fixtures_match_operative_evidence`, first in file |
| `expert_time_estimate_min` | J1.7 / J4.7 | 180 (J4's number, not J1's 150) |
| Define "live" once, before A-05 uses it | J2.1 | A-2026-06 |
| Generate `registry.json`, don't hand-write | J4.1 | `tools/gen_registry.py`, outside `environment/` |
| Pre-API terminal verdicts contact no API | J2.3 | One sentence in policy body |
| `amendment_key_id` null-handling | J2.4 | A-2026-05 states a null `amendment_key_id` is not live |
| Ablation asserts "differs at a named artifact" | J2.5 | Never whole-dict inequality |
| Cut ablation toggles 4 → 3 | J4.4 | `enforce_transitive_voiding`, `enforce_compromise_backdating`, `enforce_channel_exposure` |
| Delete `art-beta` hardcode in ApiServer | J2.2, J4.5 | Explicit `canonical_digest` on every record |
| Plain `CREATE TABLE`, not `ALTER` | J3.5 (design #2) | Confirmed: DB is built at image build |
| Digest prefixes must be distinct | J2.7 | `RPAD(prefix8, 64, '0')`, 8-char prefixes unique |
| Bump `platform-revision` | J3.4 | `2026-07-20-r1` |
| Instruction stays 3 short paragraphs | J3.1/J3.2 | ~270 words, killer mechanics named, no rules given |

**Explicitly rejected:** design #2's bundle graph (cost), design #3's run-instant evaluation and rotation pairs (fatal + spec surface), design #4 entirely, `reinstate` events (J4.4 on design #3: cut it), retry budgets, and any status-code table anywhere.

---

# 2. FILE-BY-FILE CHANGES

## 2.1 `environment/attestation-db/schema.sql` (full replacement)

```sql
-- Release attestation store. H2 is canonical for signing evidence and key history.

CREATE TABLE release_channels (
  channel_id VARCHAR(32) PRIMARY KEY,
  name       VARCHAR(64) NOT NULL
);

CREATE TABLE artifacts (
  artifact_id VARCHAR(64) PRIMARY KEY,
  channel_id  VARCHAR(32) NOT NULL,
  version     VARCHAR(32) NOT NULL,
  CONSTRAINT fk_a_channel FOREIGN KEY (channel_id) REFERENCES release_channels(channel_id)
);

CREATE TABLE signing_keys (
  key_id     VARCHAR(32) PRIMARY KEY,
  subject    VARCHAR(64) NOT NULL,
  not_before TIMESTAMP NOT NULL,
  not_after  TIMESTAMP NOT NULL
);

CREATE TABLE key_lifecycle_events (
  event_id       VARCHAR(64) PRIMARY KEY,
  key_id         VARCHAR(32) NOT NULL,
  event_type     VARCHAR(16) NOT NULL,
  reason         VARCHAR(32),
  occurred_at    TIMESTAMP NOT NULL,
  effective_from TIMESTAMP,
  CONSTRAINT fk_kle_key FOREIGN KEY (key_id) REFERENCES signing_keys(key_id),
  CONSTRAINT ck_kle_type CHECK (event_type IN ('activate', 'revoke'))
);

CREATE TABLE timestamp_authorities (
  tsa_id      VARCHAR(32) PRIMARY KEY,
  name        VARCHAR(64) NOT NULL,
  valid_from  TIMESTAMP NOT NULL,
  valid_until TIMESTAMP NOT NULL
);

CREATE TABLE artifact_evidence (
  evidence_id            VARCHAR(64) PRIMARY KEY,
  artifact_id            VARCHAR(64) NOT NULL,
  sha256_digest          VARCHAR(64) NOT NULL,
  signer_key_id          VARCHAR(32) NOT NULL,
  signed_at              TIMESTAMP NOT NULL,
  recorded_at            TIMESTAMP NOT NULL,
  status                 VARCHAR(16) NOT NULL,
  supersedes_evidence_id VARCHAR(64),
  amendment_key_id       VARCHAR(32),
  tsa_id                 VARCHAR(32),
  CONSTRAINT fk_ae_artifact  FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id),
  CONSTRAINT fk_ae_signer    FOREIGN KEY (signer_key_id) REFERENCES signing_keys(key_id),
  CONSTRAINT fk_ae_amender   FOREIGN KEY (amendment_key_id) REFERENCES signing_keys(key_id),
  CONSTRAINT fk_ae_tsa       FOREIGN KEY (tsa_id) REFERENCES timestamp_authorities(tsa_id),
  CONSTRAINT ck_ae_status    CHECK (status IN ('attested', 'provisional', 'withdrawn'))
);

CREATE TABLE pending_attestations (
  queue_id    VARCHAR(64) PRIMARY KEY,
  artifact_id VARCHAR(64) NOT NULL,
  enqueued_at TIMESTAMP NOT NULL,
  CONSTRAINT fk_pa_artifact FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id)
);

CREATE TABLE attestation_reports (
  artifact_id VARCHAR(64) PRIMARY KEY,
  verdict     VARCHAR(16) NOT NULL,
  reason_code VARCHAR(64) NOT NULL,
  checked_at  TIMESTAMP NOT NULL,
  CONSTRAINT fk_ar_artifact FOREIGN KEY (artifact_id) REFERENCES artifacts(artifact_id),
  CONSTRAINT ck_ar_verdict  CHECK (verdict IN ('trusted', 'denied', 'quarantine'))
);
```

Two deliberate changes beyond the new tables: `artifact_evidence.revoked` is **gone** (revocation is only derivable), and the `pending_attestations` / `attestation_reports` foreign keys now point at `artifacts`, not `artifact_evidence` — which is what finally makes `missing_evidence` reachable. It is dead spec today.

The FKs on `signer_key_id`, `amendment_key_id`, and `tsa_id` are load-bearing for *sufficiency*: they make "operative row names a key that does not exist" impossible by construction, so the policy needs no fail-closed rule for it and no untested reason code.

## 2.2 `environment/attestation-db/seed.sql` (full replacement)

Channels are `stable` and `edge`. I renamed `beta` to `edge` because `art-beta` sitting in a channel called `beta` while a *different* channel is the exposed one is genuinely confusing to read.

```sql
INSERT INTO release_channels (channel_id, name) VALUES
  ('stable', 'Stable'),
  ('edge',   'Edge');

INSERT INTO signing_keys (key_id, subject, not_before, not_after) VALUES
  ('key-a', 'Release Engineering', TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00'),
  ('key-b', 'Packaging',           TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2026-02-15 00:00:00'),
  ('key-c', 'Build Farm',          TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2026-02-01 00:00:00'),
  ('key-d', 'Legacy Mirror',       TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00');

INSERT INTO key_lifecycle_events (event_id, key_id, event_type, reason, occurred_at, effective_from) VALUES
  ('kev-001', 'key-a', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-002', 'key-b', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-003', 'key-c', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-004', 'key-d', 'activate', NULL,                     TIMESTAMP '2025-01-01 00:00:00', NULL),
  ('kev-005', 'key-c', 'revoke',   'key_compromise',         TIMESTAMP '2026-03-05 12:00:00', TIMESTAMP '2026-01-10 00:00:00'),
  ('kev-006', 'key-d', 'revoke',   'cessation_of_operation', TIMESTAMP '2026-02-20 09:00:00', TIMESTAMP '2025-06-01 00:00:00');

INSERT INTO timestamp_authorities (tsa_id, name, valid_from, valid_until) VALUES
  ('tsa-1', 'Corp TSA', TIMESTAMP '2025-01-01 00:00:00', TIMESTAMP '2027-01-01 00:00:00');

INSERT INTO artifacts (artifact_id, channel_id, version) VALUES
  ('art-alpha',   'stable', '2.4.1'),
  ('art-beta',    'stable', '2.4.0'),
  ('art-gamma',   'stable', '2.5.0'),
  ('art-delta',   'stable', '2.3.9'),
  ('art-epsilon', 'edge',   '1.9.0'),
  ('art-zeta',    'edge',   '1.9.1'),
  ('art-omega',   'edge',   '1.9.2'),
  ('art-eta',     'stable', '1.8.2'),
  ('art-theta',   'stable', '2.6.0'),
  ('art-iota',    'stable', '2.6.1'),
  ('art-kappa',   'edge',   '1.9.3'),
  ('art-mu',      'stable', '2.7.0'),
  ('art-lambda',  'stable', '2.7.1'),
  ('art-nu',      'stable', '2.7.2');

INSERT INTO artifact_evidence
  (evidence_id, artifact_id, sha256_digest, signer_key_id, signed_at, recorded_at,
   status, supersedes_evidence_id, amendment_key_id, tsa_id) VALUES
  ('ev-a1', 'art-alpha',   RPAD('a1a1a1a1', 64, '0'), 'key-a', TIMESTAMP '2026-02-10 08:00:00', TIMESTAMP '2026-02-10 08:05:00', 'attested',    NULL,    NULL,    NULL),

  ('ev-b1', 'art-beta',    RPAD('b1b1b1b1', 64, '0'), 'key-a', TIMESTAMP '2026-01-15 08:00:00', TIMESTAMP '2026-01-15 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-b2', 'art-beta',    RPAD('b2b2b2b2', 64, '0'), 'key-a', TIMESTAMP '2026-02-18 08:00:00', TIMESTAMP '2026-02-18 08:05:00', 'attested',    'ev-b1', 'key-a', NULL),

  ('ev-g1', 'art-gamma',   RPAD('c1c1c1c1', 64, '0'), 'key-a', TIMESTAMP '2026-01-05 08:00:00', TIMESTAMP '2026-01-05 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-g2', 'art-gamma',   RPAD('c2c2c2c2', 64, '0'), 'key-a', TIMESTAMP '2026-01-20 08:00:00', TIMESTAMP '2026-01-20 08:05:00', 'attested',    'ev-g1', 'key-a', NULL),
  ('ev-g3', 'art-gamma',   RPAD('c3c3c3c3', 64, '0'), 'key-a', TIMESTAMP '2026-02-02 08:00:00', TIMESTAMP '2026-02-02 08:05:00', 'withdrawn',   'ev-g2', 'key-a', NULL),

  ('ev-d1', 'art-delta',   RPAD('d1d1d1d1', 64, '0'), 'key-a', TIMESTAMP '2026-02-01 08:00:00', TIMESTAMP '2026-02-01 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-d2', 'art-delta',   RPAD('d2d2d2d2', 64, '0'), 'key-a', TIMESTAMP '2026-03-10 08:00:00', TIMESTAMP '2026-03-10 08:05:00', 'attested',    'ev-d1', 'key-c', NULL),

  ('ev-e1', 'art-epsilon', RPAD('e1e1e1e1', 64, '0'), 'key-c', TIMESTAMP '2026-01-20 08:00:00', TIMESTAMP '2026-01-20 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-z1', 'art-zeta',    RPAD('f1f1f1f1', 64, '0'), 'key-c', TIMESTAMP '2026-01-05 08:00:00', TIMESTAMP '2026-01-05 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),
  ('ev-o1', 'art-omega',   RPAD('0a0a0a0a', 64, '0'), 'key-c', TIMESTAMP '2026-01-06 08:00:00', TIMESTAMP '2026-01-06 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-k1', 'art-kappa',   RPAD('4e4e4e4e', 64, '0'), 'key-c', TIMESTAMP '2026-02-05 08:00:00', TIMESTAMP '2026-02-05 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),

  ('ev-h1', 'art-eta',     RPAD('1b1b1b1b', 64, '0'), 'key-d', TIMESTAMP '2026-01-15 08:00:00', TIMESTAMP '2026-01-15 08:05:00', 'attested',    NULL,    NULL,    NULL),

  ('ev-t1', 'art-theta',   RPAD('2c2c2c2c', 64, '0'), 'key-b', TIMESTAMP '2026-03-01 08:00:00', TIMESTAMP '2026-03-01 08:05:00', 'attested',    NULL,    NULL,    NULL),
  ('ev-i1', 'art-iota',    RPAD('3d3d3d3d', 64, '0'), 'key-b', TIMESTAMP '2026-03-02 08:00:00', TIMESTAMP '2026-03-02 08:05:00', 'attested',    NULL,    NULL,    'tsa-1'),

  ('ev-m1', 'art-mu',      RPAD('5f5f5f5f', 64, '0'), 'key-a', TIMESTAMP '2026-02-11 08:00:00', TIMESTAMP '2026-02-11 08:05:00', 'provisional', NULL,    NULL,    NULL),

  ('ev-n1', 'art-nu',      RPAD('6a6a6a6a', 64, '0'), 'key-a', TIMESTAMP '2026-02-12 08:00:00', TIMESTAMP '2026-02-12 08:05:00', 'attested',    NULL,    NULL,    NULL);

INSERT INTO pending_attestations (queue_id, artifact_id, enqueued_at) VALUES
  ('q-001', 'art-alpha',   TIMESTAMP '2026-03-20 09:00:00'),
  ('q-002', 'art-beta',    TIMESTAMP '2026-03-20 09:01:00'),
  ('q-003', 'art-gamma',   TIMESTAMP '2026-03-20 09:02:00'),
  ('q-004', 'art-delta',   TIMESTAMP '2026-03-20 09:03:00'),
  ('q-005', 'art-epsilon', TIMESTAMP '2026-03-20 09:04:00'),
  ('q-006', 'art-zeta',    TIMESTAMP '2026-03-20 09:05:00'),
  ('q-007', 'art-omega',   TIMESTAMP '2026-03-20 09:06:00'),
  ('q-008', 'art-eta',     TIMESTAMP '2026-03-20 09:07:00'),
  ('q-009', 'art-theta',   TIMESTAMP '2026-03-20 09:08:00'),
  ('q-010', 'art-iota',    TIMESTAMP '2026-03-20 09:09:00'),
  ('q-011', 'art-kappa',   TIMESTAMP '2026-03-20 09:10:00'),
  ('q-012', 'art-mu',      TIMESTAMP '2026-03-20 09:11:00'),
  ('q-013', 'art-lambda',  TIMESTAMP '2026-03-20 09:12:00'),
  ('q-014', 'art-nu',      TIMESTAMP '2026-03-20 09:13:00');
```

`RPAD(prefix, 64, '0')` removes any chance of hand-miscounting a 64-char literal, and every 8-char prefix is unique, which matters because `ApiServer.expectedSignature` keys the signature off `digest.substring(0, 8)`.

`kev-006` is the planted foot-gun: a non-null `effective_from` on a `cessation_of_operation` revoke that A-2026-08 says to disregard. It exists specifically to punish `COALESCE(effective_from, occurred_at)`, which is the idiomatic read off the column names.

**Traced expected verdicts (shipped store):**

| Artifact | Verdict | reason_code | Mechanic |
|---|---|---|---|
| art-alpha | denied | `bad_signature` | API layer |
| art-beta | trusted | `verified` | amendment supersedes (M1) |
| art-gamma | quarantine | `no_operative_evidence` | void fixpoint + withdrawn tip (M2) |
| art-delta | trusted | `verified` | unauthorised amendment discarded, voids nothing (M3) |
| art-epsilon | denied | `revoked_signer` | compromise backdating bites (M4) |
| art-zeta | trusted | `verified` | compromise does not reach back + exposure exemption (M5/M11a) |
| art-omega | quarantine | `channel_exposure` | exposure downgrade (M11b) |
| art-eta | trusted | `verified` | non-compromise revoke does not backdate (M6) |
| art-theta | denied | `expired_key_signature` | validity window (M7) |
| art-iota | trusted | `verified` | countersignature survives expiry (M8) |
| art-kappa | denied | `revoked_signer` | revocation settled before expiry (M9) |
| art-mu | quarantine | `no_operative_evidence` | rows exist, none operative (M10a) |
| art-lambda | quarantine | `missing_evidence` | no rows at all (M10b) |
| art-nu | quarantine | `verify_degraded` | API layer |

5 trusted, 4 denied, 5 quarantine.

The pairs are what carry the difficulty, and they should be read as pairs: `art-zeta`/`art-epsilon` sit on opposite sides of one compromise boundary with the same key; `art-theta`/`art-iota` differ only by a `tsa_id`; `art-kappa` is `art-iota`'s countersignature meeting `art-epsilon`'s revocation, so it only makes sense next to both; `art-zeta`/`art-omega` differ only by a countersignature and are the entire exposure mechanic.

## 2.3 `environment/policy/signing-trust-policy.md` (rewrite — the `## HTTP mapping` table is deleted)

```markdown
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
```

Every one of the thirteen reason codes appears as a backticked literal. That is the fix that kills design #2's fatal, and it is the single cheapest thing on this list to get wrong.

## 2.4 `environment/policy/signing-trust-amendments.md` (new)

```markdown
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

A row whose `supersedes_evidence_id` is non-null voids the row it references. Then
void any row whose `evidence_id` equals a voided row's `supersedes_evidence_id`,
repeating until the void set stops growing. This is settled before A-2026-02
selects.

## A-2026-04 - a superseding row voids regardless of its own standing

Voiding under A-2026-03 follows from the reference alone. A `withdrawn` or
`provisional` row voids what it supersedes even though A-2026-02 will never let it
become operative.

An artifact whose every row is void, discarded, or not `attested` has no operative
evidence and is recorded `quarantine` with reason_code `no_operative_evidence`.
That is a different outcome from `missing_evidence`, which is only for an artifact
with no `artifact_evidence` rows at all.

## A-2026-05 - amendment authority

A row with a non-null `supersedes_evidence_id` is an amendment, and
`amendment_key_id` is the key that authorised it. The amendment is discarded unless
that key was live, as A-2026-06 defines live, as of the amendment row's own
`recorded_at`. A null `amendment_key_id` is not live.

A discarded amendment is not operative under A-2026-02 and voids nothing under
A-2026-03. It loses its voiding power, not only its candidacy, so the row it names
stands. Amendment authority is settled before A-2026-03 computes the void set.

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
Artifacts count towards this whether or not they appear in `pending_attestations`.

Exposure is arbitrated after every artifact already has a verdict. It downgrades a
`trusted` verdict to `quarantine` with reason_code `channel_exposure` and does
nothing else. It never changes a `denied` verdict, never changes a verdict that is
already `quarantine`, and never promotes anything.

An artifact in an exposed channel keeps its `trusted` verdict when its operative row
names a `tsa_id` whose window covers that row's `signed_at` and that `signed_at` is
strictly earlier than the instant the channel became exposed.
```

Note what is **not** here: no case-to-output grid anywhere, no worked example, no artifact id, no key id, no timestamp, no seed value, no numbered end-to-end procedure. Ordering is conveyed only through override language ("settled before A-2026-03 computes", "This is settled before A-2026-10"), so the agent still assembles the pipeline. Every term is anchored to a named column, which is the property that keeps composition-only difficulty from turning into guesswork.

The three counterintuitive rules are stated flatly and deliberately, because each is a 0/10 risk otherwise: A-2026-04 (a withdrawn row still voids), A-2026-05 (a discarded amendment loses its voiding power, so the row underneath stands), A-2026-08 (`effective_from` disregarded on non-compromise reasons). Knowing each rule still leaves the whole composition to do.

## 2.5 `instruction.md` (full replacement, exact text)

```markdown
The release attestation worker at `/app/attest-worker` issues trust decisions for signed release artifacts, and right now it believes the artifact registry instead of the signing evidence. Registry metadata can lag or disagree with what was actually signed, so a stale or tampered registry entry can get an artifact marked trusted. Make the worker decide trust from canonical signing evidence, following `/app/policy/signing-trust-policy.md` and the amendments in `/app/policy/signing-trust-amendments.md`, which override the body wherever they disagree.

`artifact_evidence` in `jdbc:h2:file:/app/attestation-db/attestation` is authoritative, but it is an amendment log rather than one row per artifact, so the worker has to settle which row is operative before it knows an artifact's digest or who signed it. Revocation is not a column any more, it is a fact about a key at an instant, and a compromised key does not stop at the artifacts it signed. Work the amendments through A-2026-11. The ones people miss are what a withdrawn amendment still does to the row underneath it, which revocations reach back behind signatures already made, and the channel pass that runs after every artifact already has a verdict. The detached signature still comes from `GET /artifacts/{id}` on the bundled metadata API on port 8080 (`bash /app/start-api.sh` if needed), and the registry never supplies the digest. Process every row in `pending_attestations` without deleting them, and record one row per artifact in `attestation_reports` with verdict `trusted`, `denied`, or `quarantine` plus the reason_code the policy assigns.

Build with `/app/attest-worker/build.sh` and run `com.snorkel.attest.Main`. It takes an optional JDBC URL; the default is the store above, and reports are always written from and to whichever store it was given.
```

274 words, three paragraphs, no bullets, no headings, no em dashes, absolute paths throughout. Paragraphs 1 and 3 reuse Fabrice's existing sentences almost verbatim; only paragraph 2 is new. It names every killer mechanic without stating a single rule, which is the same move the reference makes with "The usual misses are in the group arbitration."

Run the authorship scans from `authorship.mdc` before shipping:

```bash
rg -n $'—|–' enforce-java-release-signature-trust/instruction.md
rg -in 'really|deliverable|as follows|the following|ensure that|in order to|note that|utilize|robust|seamless|comprehensive' enforce-java-release-signature-trust/instruction.md
rg -no '[`\w]+, [`\w]+ (and|or) ' enforce-java-release-signature-trust/instruction.md
rg -n '^\s*[-*#]' enforce-java-release-signature-trust/instruction.md
wc -w enforce-java-release-signature-trust/instruction.md
```

## 2.6 `environment/attest-worker/src/com/snorkel/attest/Worker.java` (broken scaffold)

The scaffold must get *smaller* and more plausibly wrong. It must compile and run to completion against the new schema, and it must not hint at any mechanic.

Keep unchanged: `writeReport`, `httpGet`, `httpPostVerify`, `readStream`, `HttpResult`, `PendingRow`, `loadPending`.

Change:

- `loadEvidence` becomes a single-row read that compiles against the new schema and looks reasonable:
  ```java
  "SELECT sha256_digest, signer_key_id FROM artifact_evidence "
      + "WHERE artifact_id = ? ORDER BY recorded_at DESC LIMIT 1"
  ```
  It cannot select `revoked` any more, because the column is gone. This is the plausible-looking wrong answer: it ignores void, status, and amendment authority all at once.
- `Evidence` record drops `revoked`, becomes `record Evidence(String sha256Digest, String signerKeyId) {}`.
- No key tables, no TSA table, no `artifacts` table are loaded at all. The agent's first act is discovering that the schema no longer matches the code it was handed, which is where the exploration budget should go.
- Revocation keeps being read off the registry JSON (`registry.path("revoked").asBoolean(false)`), which preserves the "believes the registry" story in the instruction. `registry.json` contains no `revoked` key on any record, so the branch always falls through, exactly as today.
- Keeps sending `registry.path("registry_digest")` to verify, preserving the original bug.
- Keeps the `409 -> trusted/digest_accepted` and `404 -> quarantine/unknown_artifact` mismappings.
- No exposure pass, no second phase.

Verify with `javac` inside the task image. `codebase_applicability` stays green and nothing leaks.

## 2.7 `solution/attest-worker/src/com/snorkel/attest/Worker.java` (oracle)

166 → roughly 400 lines. The growth is structural, not a longer branch list. `writeReport`, `httpGet`, `httpPostVerify`, `readStream` survive untouched.

New records: `Key(keyId, subject, notBefore, notAfter)`, `KeyEvent(eventId, keyId, type, reason, occurredAt, effectiveFrom)`, `Tsa(tsaId, validFrom, validUntil)`, `EvidenceRow(evidenceId, artifactId, digest, signerKeyId, signedAt, recordedAt, status, supersedesId, amendmentKeyId, tsaId)`, `Verdict(String verdict, String reasonCode)`.

New methods:

| Method | Lines | Does |
|---|---|---|
| `loadKeys(conn)` → `Map<String,Key>` | ~18 | validity windows |
| `loadKeyEvents(conn)` → `Map<String,List<KeyEvent>>` | ~25 | grouped per key |
| `loadTsas(conn)` → `Map<String,Tsa>` | ~15 | |
| `loadArtifactChannels(conn)` → `Map<String,String>` | ~15 | |
| `loadAllEvidence(conn)` → `Map<String,List<EvidenceRow>>` | ~30 | whole chain per artifact, one query |
| `effectiveInstant(KeyEvent)` | ~8 | A-2026-08, reason-dependent |
| `revokedAt(keyId, LocalDateTime)` | ~25 | A-2026-07 replay, comparator with `event_id` tie-break |
| `isLive(keyId, LocalDateTime)` | ~8 | A-2026-06 |
| `tsaCovers(tsaId, LocalDateTime)` | ~8 | half-open |
| `resolveOperative(rows)` | ~60 | **the real work**: discard unauthorised amendments, seed void set from surviving `supersedes_evidence_id`, iterate to fixpoint, filter to `attested`, max by `(recordedAt, evidenceId)` |
| `evaluate(artifactId, operative)` | ~55 | A-09 → A-10 → GET → POST, returns `Verdict` instead of writing |
| `computeExposure(operativeByArtifact, channels)` | ~30 | A-2026-11 phase 1 |
| `applyExposure(verdict, artifactId, operative, exposedFrom)` | ~20 | A-2026-11 phases 2 and 3 |

`run()` becomes four explicit phases:

```
1. resolveOperative for EVERY artifact in artifact_evidence, not only queued ones
2. computeExposure over those operative rows + artifacts.channel_id
3. evaluate each queued artifact into an in-memory Map<String, Verdict>
4. applyExposure, then writeReport, then commit
```

Phase 1 running over every artifact and phase 3 running over the queue is the structural change that makes the loop body unwritable in isolation. Reports are buffered and written after the loop.

**Time handling, decided once and applied everywhere:** every policy comparison uses `java.time.LocalDateTime` obtained from `rs.getTimestamp(...).toLocalDateTime()`. H2 `TIMESTAMP` is wall-clock, `LocalDateTime` is zone-free, and the Python side compares naive `datetime`. Nothing mixes `Instant` into a comparison. The one `Instant.now()` is `checked_at`, which is never asserted on. `ENV TZ=UTC` goes in the Dockerfile as belt and braces, but correctness does not depend on it.

## 2.8 `environment/artifact-api/src/com/snorkel/attestapi/ApiServer.java`

One change only. Delete lines 184-186:

```java
if ("art-beta".equals(artifactId)) {
    canonicalDigest = "d2222222222222222222222222222222222222222222222222222222222222";
}
```

Line 183's `node.path("canonical_digest").asText(registryDigest)` fallback does the work, and every record in the regenerated `registry.json` carries an explicit `canonical_digest`. No other API change: no new endpoint, no state, no counters. That statelessness is why the verifier can call the live API to compute expectations without the run-count hazard that made design #4 fatal.

## 2.9 `environment/artifact-api/data/registry.json` (regenerated, not hand-written)

Records for all 14 shipped artifacts plus 6 variant-only artifacts (`art-live`, `art-flop`, `art-taint`, `art-quiet`, `art-clear`, `art-stamped`). Deliberately **no** record for `art-probe` (drives GET 404) and none for `art-lambda` or `art-chain` (never reached on a correct run; a wrong path lands on `unknown_artifact`, which is a usefully distinct wrong answer).

Coupling rules, all three of which must hold or the fixtures silently desync:
- `canonical_digest` = the **operative** row's `sha256_digest`
- `signer_key_id` = the **operative** row's `signer_key_id`
- `detached_signature` = `"sig-" + canonical_digest[0:8] + "-" + signer_key_id`

Three deliberate deviations:
- `art-alpha` gets `detached_signature: "sig-00000000-key-a"` (wrong) → POST 400 → `bad_signature`
- `art-nu` gets `verify_degraded: true` → POST 503 → `verify_degraded`
- `art-beta` gets `registry_digest: RPAD('99999999',64,'0')` expanded, diverging from its canonical `b2b2b2b2...` → preserves the original stale-registry lesson, and sending `registry_digest` still draws a 409

For `art-gamma`, whose correct verdict never reaches the API, set `canonical_digest` to `ev-g3`'s digest with a **matching** signature. That makes each of the three wrong resolution paths land on a *different* wrong answer: one-pass voiding → `ev-g1` → 409 `digest_mismatch`; status-filter-first → `ev-g2` → 409 `digest_mismatch`; latest-`recorded_at`-ignoring-status → `ev-g3` → 200 `trusted/verified`. All three are distinguishable from the correct `quarantine/no_operative_evidence`.

## 2.10 `tools/gen_registry.py` (new, outside `environment/`)

Judge 4's highest-value fix. Opens the built H2 store, runs the operative-row derivation, and emits `environment/artifact-api/data/registry.json` with all three coupled fields per artifact, then applies the three deliberate deviations from a small explicit override table at the top of the file. Matches the repo convention already set by the reference task's `tools/gen_build_artifacts.sh`. Never copied into the image.

## 2.11 `environment/Dockerfile`

```dockerfile
# platform-revision: 2026-07-20-r1
ENV TZ=UTC
COPY policy/signing-trust-amendments.md /app/policy/signing-trust-amendments.md
```

Nothing else changes. Base digest untouched, no new dependencies, no network.

## 2.12 `task.toml`

```toml
expert_time_estimate_min = 180
junior_time_estimate_min = 420
```

`difficulty` stays `"medium"` but must be **re-measured** over 5 runs on both frontier models before resubmission, per `terminus.mdc`. Do not carry the current value forward on the strength of the argument in section 5.

---

# 3. TRAP INVENTORY

| # | Trap | Naive behavior punished | Artifact(s) | Caught by |
|---|---|---|---|---|
| 1 | Single-row evidence read | `SELECT ... WHERE artifact_id = ?` and take the first row | art-beta, art-delta, art-gamma | `test_amendment_supersedes_predecessor` |
| 2 | Latest `recorded_at` wins | `ORDER BY recorded_at DESC LIMIT 1` picks a `withdrawn` tip or an unauthorised amendment | art-gamma, art-delta | `test_withdrawn_tip_voids_the_chain` |
| 3 | Filter to `attested`, then take latest | The careful near-miss: selects `ev-g2`, which is void because withdrawn `ev-g3` supersedes it. Producing *any* verdict here is the failure | art-gamma | `test_withdrawn_tip_voids_the_chain` |
| 4 | Single-pass voiding | Chain is 3 deep; one pass voids `ev-g2` but leaves `ev-g1` standing | art-gamma | `test_ablation_transitive_voiding_changes_a_verdict` |
| 5 | Void before checking amendment authority | `ev-d1` is destroyed before `ev-d2` is discarded → `no_operative_evidence` instead of trusted | art-delta | `test_unauthorised_amendment_is_discarded_without_voiding` |
| 6 | Skip amendment authority entirely | `ev-d2` becomes operative → wrong digest → 409 `digest_mismatch` | art-delta | same |
| 7 | Any `revoke` row means revoked | Ignores the effective instant; flips an artifact signed 5 days before the boundary | art-zeta | `test_compromise_does_not_reach_earlier_signature` |
| 8 | Evaluate key state at run time | Worker runs long after both revocations were recorded; every key-c and key-d artifact flips | art-zeta, art-eta | tests 9 and 10 |
| 9 | `COALESCE(effective_from, occurred_at)` | The idiomatic read off column names. `kev-006` backdates to 2025-06-01 and denies an artifact that must be trusted | art-eta | `test_non_compromise_revocation_does_not_backdate` |
| 10 | Validity window treated as absolute | Ignores the countersignature rescue | art-iota | `test_countersignature_survives_expiry` |
| 11 | Countersignature as a blanket rescue | Checks expiry-with-TSA before revocation. `art-kappa` is revoked *and* expired *and* countersigned, so a wrong order yields `trusted`, and dropping the TSA yields `expired_key_signature`. Three-way discrimination | art-kappa | `test_countersignature_does_not_survive_compromise` |
| 12 | Collapse `no_operative_evidence` into `missing_evidence` | A naming coin-flip that costs two artifacts | art-mu, art-lambda | `test_no_operative_evidence_differs_from_missing_evidence` |
| 13 | Skip the exposure pass | Per-artifact verdict stands, `art-omega` reads trusted | art-omega | `test_channel_exposure_downgrades_uncountersigned_trusted` |
| 14 | Exposure without the exemption | Blanket-quarantines the channel, wrongly hitting a countersigned artifact | art-zeta | same |
| 15 | Exposure applied to denied verdicts | `art-epsilon` and `art-kappa` become `channel_exposure` instead of `revoked_signer` | art-epsilon, art-kappa | same (two-sided assertion) |
| 16 | Exposure scoped from a key column | There is no `signing_keys.channel_id`; scope must be derived from artifacts' operative signers | art-quiet (variant) | `test_worker_reruns_on_channel_exposure_variant` |
| 17 | Send `registry_digest` to verify | The original lesson, preserved | art-beta | `test_registry_digest_alone_is_insufficient` |

Traps 1-6 are all silent. Pick the wrong evidence row and you do not crash: you send a real digest to a real API, get a real 409, and write `denied`/`digest_mismatch`, which is a legitimate reason code the policy defines. An agent that does not go back and question its evidence resolution gets no signal that anything is wrong. Same for trap 9: `COALESCE` compiles, runs, and silently denies an artifact that should be trusted.

---

# 4. TEST PLAN

`helpers.py` grows to roughly 480 lines. `expected_report` stops being an if/else mirror of the policy table and becomes a Python reimplementation of the derivation, recomputing expectations from whatever store it is pointed at with no hardcoded ids or digests. That alone makes hand-written reports and hardcoded lookups unpassable. It calls the live API for the final GET/POST step, exactly as it does today, which is safe because `ApiServer` holds no mutable state.

New helper surface: `load_keys`, `load_key_events`, `load_tsas`, `load_artifact_channels`, `load_evidence_rows`, `effective_instant`, `revoked_at`, `is_live`, `resolve_operative`, `compute_exposure`, `expected_reports_for_db(db_url, *, enforce_transitive_voiding=True, enforce_compromise_backdating=True, enforce_channel_exposure=True)`.

| # | Test | Verifies | Made fair by | 0/10 risk |
|---|---|---|---|---|
| 1 | `test_registry_fixtures_match_operative_evidence` | Authoring guard: registry `canonical_digest` / `signer_key_id` / `detached_signature` agree with the derived operative row. **First in the file** | n/a (precondition) | none |
| 2 | `test_api_serves_health` | keep | n/a | none |
| 3 | `test_reports_cover_every_pending_artifact` | keep | instruction para 2 | none |
| 4 | `test_shipped_reports_match_policy` | All 14 artifacts, all-or-nothing | whole policy | none |
| 5 | `test_amendment_supersedes_predecessor` | art-beta trusted, not `digest_mismatch` | A-01, A-02, A-03 | low |
| 6 | `test_withdrawn_tip_voids_the_chain` | art-gamma `no_operative_evidence` | **A-2026-04** | **HIGHEST** |
| 7 | `test_unauthorised_amendment_is_discarded_without_voiding` | art-delta trusted from `ev-d1` | **A-2026-05** (both consequences) | **HIGH** |
| 8 | `test_compromise_backdating_denies_later_signature` | art-epsilon `revoked_signer` | A-07, A-08, A-09 | low |
| 9 | `test_compromise_does_not_reach_earlier_signature` | art-zeta trusted | A-08, A-09 | low |
| 10 | `test_non_compromise_revocation_does_not_backdate` | art-eta trusted | **A-2026-08** ("disregarded") | **MEDIUM** |
| 11 | `test_expired_key_signature_denied` | art-theta `expired_key_signature` | A-10 | low |
| 12 | `test_countersignature_survives_expiry` | art-iota trusted | A-10 | low |
| 13 | `test_countersignature_does_not_survive_compromise` | art-kappa `revoked_signer` | **A-09 "settled before A-10"** | **MEDIUM** |
| 14 | `test_no_operative_evidence_differs_from_missing_evidence` | art-mu vs art-lambda | **A-2026-04** (same sentence) | **MEDIUM** |
| 15 | `test_channel_exposure_downgrades_uncountersigned_trusted` | art-omega quarantined **and** art-epsilon still denied | **A-2026-11** | **MEDIUM** |
| 16 | `test_ablation_transitive_voiding_changes_a_verdict` | Fixpoint is load-bearing at art-gamma | n/a | none |
| 17 | `test_ablation_compromise_backdating_changes_a_verdict` | Backdating is load-bearing at art-epsilon | n/a | none |
| 18 | `test_ablation_channel_exposure_changes_a_verdict` | Exposure is load-bearing at art-omega | n/a | none |
| 19 | `test_worker_reruns_on_unknown_artifact_variant` | art-probe `unknown_artifact` | policy API outcomes | none |
| 20 | `test_worker_reruns_on_deep_chain_variant` | Depth-4 fixpoint + `provisional` tip; art-live trusted | A-03, A-04 | low |
| 21 | `test_worker_reruns_on_backdated_compromise_variant` | Same artifact shape flips verdict from data alone | A-08 | low |
| 22 | `test_worker_reruns_on_channel_exposure_variant` | art-taint + art-quiet quarantined, art-clear + art-stamped trusted | A-11 | **MEDIUM** |
| 23 | `test_registry_digest_alone_is_insufficient` | keep, retargeted at art-beta's operative digest | policy canonical evidence | none |

Ablation tests 16-18 assert **"differs at this named artifact"**, never whole-dict inequality, and each toggle is hand-verified at authoring time to flip at least one shipped artifact. A toggle that changes nothing is a test that fails correct agents.

Tests 5-15 are pairs, not a list of edge cases: `art-zeta` is only meaningful next to `art-epsilon`, `art-iota` only next to `art-theta`, `art-kappa` only next to both, `art-omega` only next to `art-zeta`. Each pair isolates one rule by holding everything else constant and flipping a single fact.

**Variant seeds** (4, all verifier-built, agent never sees them, all wipe every table first):

- `variant_unknown_seed.sql` — migrated. `art-probe`, single attested row, no registry record → GET 404 → `denied/unknown_artifact`.
- `variant_chain_seed.sql` — `art-chain` with a four-deep chain (`ev-c1` ← `ev-c2` ← `ev-c3` ← `ev-c4`) whose tip is `provisional`. Fixpoint depth exceeds the shipped store's 3, and it uses a status the shipped store only uses once. Plus `art-live`, single attested row → trusted, so the variant is not uniformly quarantine.
- `variant_backdate_seed.sql` — key-c compromise with `effective_from` moved to 2026-01-01. `art-flip` signed 2026-01-05 → `denied/revoked_signer` (the same signing date is trusted in the shipped store). `art-flop` signed 2025-12-20 with `tsa-1` → trusted and exempt. Proves backdating is read from data, not hardcoded.
- `variant_exposure_seed.sql` — the sharp one. `art-taint` (key-c, compromised, edge) → quarantined; **`art-quiet` (key-e, never revoked, edge, uncountersigned) → quarantined** because a *different artifact's* operative signer exposed the channel; `art-clear` (key-e, stable) → trusted, proving exposure is channel-scoped; `art-stamped` (key-e, edge, countersigned before the exposure instant) → trusted. Four exposure behaviours, and the only test that can distinguish artifact-derived scope from a key-column reading.

**Migration note:** the two existing variant seeds must be rewritten for the new schema. Every variant seed needs `DELETE FROM` for `artifact_evidence`, `pending_attestations`, `attestation_reports`, `key_lifecycle_events`, `artifacts`, `signing_keys`, `timestamp_authorities`, `release_channels` in FK-safe order, and must then insert its own channels, keys, TSA, and artifacts. A variant that silently inherits shipped rows passes for the wrong reason and a green suite will not catch it.

---

# 5. DIFFICULTY ARGUMENT

**Could a frontier model read the policy and write an if/else chain that passes first try? No, because no if/else chain exists.** The output is not a function of any bounded tuple of scalars the agent can read. It is a function of a fixpoint over a graph, evaluated in a specific order relative to a replay over a second table, sampled at an instant the first computation produces, and then filtered by a channel-level fact derived from *all* artifacts' operative rows.

Eight independent things must all be right simultaneously:

1. The void fixpoint iterates rather than passes once
2. A non-`attested` row still voids what it supersedes
3. Amendment authority is settled **before** voiding, not after
4. A discarded amendment loses its **voiding power**, not merely its candidacy
5. The revocation replay keys backdating off `reason` while ignoring a populated `effective_from` on the wrong reason
6. Key standing is sampled at the operative row's `signed_at`, not at run time
7. Revocation is settled **before** expiry, so the countersignature rescue cannot leak across
8. Channel exposure is scoped from artifacts' operative signers, arbitrated after per-artifact verdicts, downgrades only `trusted`, and honours the strictly-earlier countersignature exemption

Each is stated as an invariant somewhere in the amendments, so none is unfair. But each must be **composed** by the agent, and the composition order is only implied by override language. `test_shipped_reports_match_policy` is all-or-nothing across 14 artifacts. Granting a strong model 0.85 per mechanic independently, 0.85^8 ≈ **27%**. Mechanic 8 alone is closer to a coin flip because artifact-derived scope is not the intuitive reading, and mechanics 2 and 4 are the two most counterintuitive rules in the design.

**Blast radius is the reason partial credit does not rescue a run.** Missing any single mechanic flips at least two artifacts, and several flip three or four, because `key-c` is shared across `art-delta` (as amender), `art-epsilon`, `art-zeta`, `art-omega`, and `art-kappa` (as signer). One row in `key_lifecycle_events` determines the amendment resolution of one artifact and the signing verdicts of four others, on both sides of a boundary.

**The specific answer to the diversity gate's complaint.** Today `signer_key_id` is selected and never used, *even in the oracle* — the strongest possible proof that no relationship between artifacts is modelled anywhere. After this change, `art-omega` is signed by a key that is never revoked, is inside its validity window, has a single clean attested row with no amendments, and still comes out `quarantine`, because a *different artifact* was signed by a key that was later compromised. There is no way to write the loop body while thinking about one artifact. Phase 1 must run over every artifact before phase 3 can evaluate any of them.

**Why this is not the prohibited kind of hardening.** The reason-code vocabulary grows by three (`expired_key_signature`, `no_operative_evidence`, `channel_exposure`), not by ten. No status-code row is added anywhere; the ten-row table is deleted. Twelve of fourteen artifacts isolate a derivation mechanic and the remaining two cover API outcomes the policy states. Nothing is removed from the instruction, no `policy_expectations` table exists, and every mechanic is native to code signing: RFC 5280 backdated revocation with reason-scoped semantics, trusted timestamping that survives expiry but never compromise, amendment-log evidence with authority-to-amend, and compromise blast radius scoped to where the key was actually used. None of it is a reskin of the reference's waiver, quorum, or suppression-group machinery.

**Honest ceiling: solid MEDIUM, not HARD.** One Java file, ~400 lines, no concurrency, no schema authoring by the agent, and the algorithmic core is a fixpoint plus a replay. A strong model that reads the amendments carefully and thinks about ordering before writing will get it. That is the correct target: the gate needs worst-model under 60%, not best-model failure.

---

# 6. RISK REGISTER

| Risk | Severity | Mitigation |
|---|---|---|
| **Spec gap on A-2026-04 (withdrawn row still voids)** | Highest. Test 6 goes 0/10, which bounces as solvability | Stated in one unambiguous sentence, in its own amendment, with the `no_operative_evidence` / `missing_evidence` distinction drawn in the same section. Validate before building: hand a fresh model only the two policy files plus the store contents and ask for all 14 verdicts cold. If it misses art-gamma, add a clause; **do not delete the test** |
| **Spec gap on A-2026-05 (discarded amendment loses voiding power)** | High. "Discarded" alone is ambiguous | A-2026-05 states both consequences explicitly and in that order. Same cold-read validation |
| **Spec gap on A-2026-08 (`effective_from` disregarded)** | Medium | Says "disregarded", not "not used". Covered by the same cold read |
| **Spec gap on ordering** (A-05 before A-03, A-03 before A-02, A-09 before A-10) | Medium. An agent that derives all mechanics but sequences them differently gets art-delta and art-kappa wrong, which would be the author's fault | Every ordering appears as an explicit override phrase. This is the reference's exact pattern and it cleared instruction sufficiency |
| **Fixture desync between seed and `registry.json`** | High, and it presents as a baffling 0/10 rather than an authoring error | `tools/gen_registry.py` generates all three coupled fields from the derivation; `test_registry_fixtures_match_operative_evidence` runs first and fails loudly. `RPAD` removes hand-counting risk on 64-char digests |
| **Timestamp drift across the H2/JDBC boundary** | Medium | One decision applied everywhere: `LocalDateTime` in Java, naive `datetime` in Python, nothing mixed. `ENV TZ=UTC` as belt and braces |
| **Broken scaffold no longer compiles** (`revoked` column deleted) | High, and it fails every agent run while the oracle passes | Scaffold rewritten to the new schema in the same pass; `javac` verified inside the task image; `bash /app/attest-worker/build.sh` must succeed on the untouched environment image before anything else lands |
| **Variant seed silently inherits shipped rows** | Medium. Passes for the wrong reason; a green suite will not catch it | Every variant seed deletes all eight tables in FK-safe order and inserts its own channels, keys, TSA, and artifacts. Assert emptiness explicitly where cheap |
| **Reviewer reads 14 artifacts as edge-case padding** | Medium | Lead the `difficulty_explanation` with the **pair structure** (zeta/epsilon on one boundary, theta/iota/kappa on revocation-before-expiry, zeta/omega on exposure) and state the mechanic count as eight. Pre-empt the read rather than leaving the artifact count to speak for itself |
| **Verifier timeout** | Low | 14 artifacts × ~2 HTTP calls against a local in-process server, plus 4 variant runs. Seconds, against a 900s budget |
| **Oracle nondeterminism** | Low | No wall-clock dependence: every comparison is between two stored timestamps. `Instant.now()` is used only for `checked_at`, which is never asserted on |
| **Platform serves a cached build** | Low but wastes a cycle | Bump `# platform-revision: 2026-07-20-r1` |
| **Difficulty overshoot** | Low | 12 of 14 artifacts exercise exactly one mechanic each, so partial credit tracks partial understanding smoothly rather than collapsing |

---

# 7. ORDER OF WORK

**Do step 1 before writing a single line of code.** It costs an hour and it is the difference between finding a spec gap now and finding it after ~900 lines of Java, Python, and SQL.

1. **Cold-read validation.** Write `signing-trust-policy.md` and `signing-trust-amendments.md` first. Hand a fresh model *only* those two files plus the seed contents, and ask it to predict all 14 verdicts and reason codes. Fix any rule it misses by adding a clause. Do not weaken a test to accommodate a miss.

2. **Table-to-prose diff.** Before deleting the `## HTTP mapping` table, diff the replacement prose against it row by row. All ten mappings plus `missing_evidence` must survive with no ambiguity, and all thirteen reason codes must appear as backticked literals. Keep the checklist for the submission notes. This is the highest bounce risk in the plan and it bounces on *sufficiency*, not difficulty.

3. **Schema and seed.** Write `schema.sql` and `seed.sql`. Build the store locally and hand-verify the operative row for all 14 artifacts with direct SQL before trusting any code.

4. **Broken scaffold.** Rewrite `environment/.../Worker.java` to the new schema. Confirm `bash /app/attest-worker/build.sh` succeeds and the worker runs to completion on the untouched image. Do this before the oracle so `codebase_applicability` and the build are never in doubt.

5. **Oracle.** Write `solution/.../Worker.java` in the four-phase shape. Run it against the shipped store and check the 14 verdicts against the hand-derivation from step 3.

6. **`tools/gen_registry.py` and regenerate `registry.json`.** Delete the `art-beta` hardcode in `ApiServer.java`. Apply the three deliberate deviations. Re-run the oracle; the 14 verdicts must still match.

7. **Python reimplementation.** Port `resolve_operative` / `revoked_at` / `compute_exposure` into `helpers.py`, keeping method boundaries identical to the Java so a divergence is diffable side by side. Add the three ablation toggles and hand-verify each flips at least one shipped artifact.

8. **Tests.** `test_registry_fixtures_match_operative_evidence` first in the file, then the mechanic tests, then the ablations, then the variants. Migrate the two existing variant seeds and write the two new ones.

9. **Dockerfile, `task.toml`, instruction.** `ENV TZ=UTC`, `COPY` the amendments, bump `platform-revision`. Set the time estimates. Ship the new `instruction.md` and run the authorship scans from section 2.5, reporting their output plus word and paragraph counts.

10. **`harbor run -a oracle -p enforce-java-release-signature-trust` to green.** Then re-run it after *every* subsequent edit, no matter how small.

11. **Re-measure difficulty** over 5 runs on both frontier models. Set `task.toml` `difficulty` from the measurement, not from section 5's argument.

12. **Commit and push** on the current branch, message `terminus: harden signature-trust task with amendment chains and key lifecycle`, author Fabrice only.

**Files touched:** `instruction.md`, `task.toml`, `environment/Dockerfile`, `environment/policy/signing-trust-policy.md`, `environment/policy/signing-trust-amendments.md` (new), `environment/attestation-db/{schema,seed}.sql`, `environment/attest-worker/src/com/snorkel/attest/Worker.java`, `environment/artifact-api/src/com/snorkel/attestapi/ApiServer.java`, `environment/artifact-api/data/registry.json`, `solution/attest-worker/src/com/snorkel/attest/Worker.java`, `tests/{helpers.py,conftest.py,test_outputs.py}`, `tests/variant_{unknown,chain,backdate,exposure}_seed.sql`, `tools/gen_registry.py` (new). `solution/solve.sh`, `tests/test.sh`, `environment/start-api.sh`, and `environment/entrypoint.sh` are unchanged.