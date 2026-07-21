# Object attestation policy

The store attests the integrity of every object in its custody. To attest an
object is to prove that the bytes it still holds are the bytes that were declared
for it. The store fails closed: it refuses to vouch for anything it cannot prove.

## The declaration and the copies in custody

Each object row is the declaration the object was accepted under. `size_bytes` is
the length that was declared and `declared_digest` under `digest_algo` is the
digest that was declared. The declaration is the evidence every verdict is proven
against, and it does not change.

The bytes are retained in up to two copies, and a copy can be tampered with,
truncated, or lost while the declaration still stands:

- the **chunk map**, the rows in `object_chunks` for the object, read as the
  `chunk_path` files in `ordinal` order, and
- the **materialised blob**, the single file at `blob_path`.

Neither copy is trusted ahead of the other. A copy counts as evidence only when it
can be read in full: the chunk map when every `chunk_path` file is present, the
blob when its file is present.

## Verdicts

Every object resolves to exactly one verdict, decided in this order.

1. Set aside any copy that does not read back at the declared `size_bytes`; a copy
   of the wrong length has been truncated or tampered and no longer stands for the
   object. If no readable copy survives at the declared length, the object is
   **unattestable** with reason `missing_content`: the store can no longer produce
   the bytes it declared, and it refuses to vouch for what it cannot produce.
2. Otherwise, if `digest_algo` is not sha256 the object is **unattestable** with
   reason `unsupported_digest`. The store trusts only sha256; a weaker or unknown
   digest is not proof of integrity, whatever the bytes hash to.
3. Otherwise, if any surviving copy hashes under sha256 to `declared_digest`, the
   object is **intact**. One copy that still proves out is enough to vouch for the
   object, so a tampered or missing chunk map does not condemn an object whose blob
   still holds the declared content, and a tampered or missing blob does not condemn
   one whose chunk map still does.
4. Otherwise the object is **corrupt** with reason `digest_mismatch`: a copy of the
   declared length survives, but its content has been altered away from what was
   declared.

Length is proven before the digest on purpose. A copy that is truncated, half
written, or padded will not match `size_bytes`, and it is set aside rather than
hashed, so a tampered copy can neither clear an object nor condemn one on its own.

## The attestation cache

`attestation_cache` holds the last `status` the store reported for each object. It
is a record of past claims, not proof of present integrity, and it is known to
drift. Every verdict is proven afresh from the bytes. An object is a **conflict**
when the proven verdict contradicts the cache: a `verified` row over an object that
proves out as anything other than intact, or a `failed` row over an object that
proves out as anything other than corrupt.

## Recorded outcome

The attestation is recorded at `/app/build/attestation-report.json` with `intact`,
`corrupt`, `unattestable`, and `conflicts` at the top level. `intact` is a list of
object ids. Each `corrupt` and `unattestable` entry carries `object_id` and a
`reason`: `corrupt` is always `digest_mismatch`, and `unattestable` is
`missing_content` when no copy survives at the declared length or
`unsupported_digest` when the declared algorithm is not sha256. Each `conflicts`
entry carries `object_id`, `cache_status` for what the store asserts (`verified` or
`failed`), and `actual_status` for the proven verdict (`intact`, `corrupt`, or
`unattestable`). No other keys appear at any level. The record is a set of verdicts
and never contains reconstructed object bytes.
