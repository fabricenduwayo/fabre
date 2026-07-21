# Object attestation policy

The store attests the integrity of every object in its custody. To attest an
object is to prove that the bytes it still holds are the bytes that were declared
for it. The store fails closed: it refuses to vouch for anything it cannot prove.

Its attestation has become unreliable and has to be re-established. The reference
attestor at `/app/ref/attest-ref.jar` reaches the verdict the store should report
for every object; how it reaches each verdict from the declaration and the copies
the store kept is the behaviour to match. This policy fixes the verdicts it can
reach and the shape of the record; the rule that assigns them is the reference's.

## Verdicts

Every object resolves to exactly one verdict.

- **intact**: the store can still prove the object holds its declared content.
- **corrupt**: the store holds content of the object, but it has been altered away
  from what was declared.
- **unattestable**: the store cannot prove the declared content at all, so it
  refuses to vouch for the object.

## The attestation cache

`attestation_cache` holds the last `status` the store reported for each object. It
is a record of past claims, not proof of present integrity, and it has drifted.
Every verdict is proven afresh from the bytes, and an object whose proven verdict
contradicts the cache is a **conflict**.

## Recorded outcome

The attestation is recorded at `/app/build/attestation-report.json` with `intact`,
`corrupt`, `unattestable`, and `conflicts` at the top level. `intact` is a list of
object ids. Each `corrupt` and `unattestable` entry carries `object_id` and a
`reason`, one of `digest_mismatch`, `missing_content`, or `unsupported_digest`.
Each `conflicts` entry carries `object_id`, `cache_status` for what the store
asserts (`verified` or `failed`), and `actual_status` for the proven verdict
(`intact`, `corrupt`, or `unattestable`). No other keys appear at any level. The
record is a set of verdicts and never contains reconstructed object bytes.
