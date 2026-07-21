# Object attestation policy

The store attests the integrity of every object it holds. An attestation is a
judgment about whether an object's stored bytes still match what was declared for
it. The store fails closed: an object it cannot vouch for is never reported as
sound.

## What is declared and what is stored

Each object row declares the object: `size_bytes` is its length and
`declared_digest` under `digest_algo` is its digest. The declaration is the fixed
truth the object is judged against.

The bytes themselves are held in up to two representations, and either may drift
from the declaration over time:

- the **chunk map**, the rows in `object_chunks` for the object, whose content is
  the `chunk_path` files read in `ordinal` order, and
- the **materialised blob**, the single file at `blob_path`.

Neither is privileged. A representation is only usable when it can be read in
full: the chunk map when every one of its chunk files is present, the blob when
its file is present. An object may have both, either, or effectively neither.

## Verdicts

Every object resolves to exactly one verdict, decided in this order.

1. Take the usable representations whose length equals the declared `size_bytes`.
   If there are none, the object is **unattestable** with reason `missing_content`:
   the store can no longer produce content of the length it declared.
2. Otherwise, if `digest_algo` is not sha256 the object is **unattestable** with
   reason `unsupported_digest`. Only sha256 is accepted; a weaker or unknown
   digest is not evidence the store is willing to vouch for, whatever the bytes
   hash to.
3. Otherwise, if any of those declared-length representations hashes under sha256
   to `declared_digest`, the object is **intact**. One sound copy is enough to
   vouch for the object, so a stale or missing chunk map does not condemn an
   object whose blob still holds the declared content, and a stale blob does not
   condemn one whose chunk map still does.
4. Otherwise the object is **corrupt** with reason `digest_mismatch`: the store
   holds content of the declared length that does not match the declared digest.

Length is checked before the digest on purpose. A copy that is stale, truncated,
or half-materialised will not match `size_bytes`, and such a copy is set aside
rather than hashed, so it can neither pass an object nor fail one on its own.

## The attestation cache

`attestation_cache` keeps the last `status` the store reported for each object. It
is a record of past claims, not evidence of current integrity, and it is known to
drift. Every verdict is recomputed from the bytes. An object is a **conflict**
when its recomputed verdict contradicts the cache: a `verified` row over an object
that recomputes to anything other than intact, or a `failed` row over an object
that recomputes to anything other than corrupt.

## Recorded outcome

The auditor records its findings at `/app/build/attestation-report.json` with
`intact`, `corrupt`, `unattestable`, and `conflicts` at the top level. `intact`
is a list of object ids. Each `corrupt` and `unattestable` entry carries
`object_id` and a `reason`: `corrupt` is always `digest_mismatch`, and
`unattestable` is `missing_content` when no declared-length copy can be read or
`unsupported_digest` when the declared algorithm is not sha256. Each `conflicts`
entry carries `object_id`, `cache_status` for what the store asserts (`verified`
or `failed`), and `actual_status` for the recomputed verdict (`intact`, `corrupt`,
or `unattestable`). No other keys appear at any level. The findings are verdicts
and never contain reconstructed object bytes.
