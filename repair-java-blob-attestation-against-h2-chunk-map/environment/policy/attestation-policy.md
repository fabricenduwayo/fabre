# Object attestation policy

The store attests the integrity of every object it holds. An attestation is a
judgment about whether an object's stored bytes still match what was declared for
it. The store fails closed: an object it cannot vouch for is never reported as
sound.

## Verdicts

Every object resolves to exactly one verdict.

- **intact**: the object's canonical content matches its declared digest.
- **corrupt**: the canonical content is readable but does not match the declared
  digest, so the object has been altered since it was declared.
- **unattestable**: integrity cannot be established at all, either because the
  canonical content cannot be read or because the declared digest uses an
  algorithm the store does not accept.

## Accepted digests

Only sha256 is accepted for attestation. An object declared under any other
algorithm is unattestable, never intact: a weaker or unknown digest is not
evidence the store is willing to vouch for.

## The attestation cache

The store keeps the last status it reported for each object. That cache is a
record of past claims, not evidence of current integrity, and it is known to
drift. Every verdict is recomputed from the object's bytes, and an object whose
recomputed verdict contradicts the cache is a conflict that must be reported.

## Canonical content

An object's bytes are retained in more than one representation. Integrity is
judged against the representation the store treats as canonical and durable,
which is not necessarily the one that is cheapest to read back. Establishing
which representation is authoritative is part of attesting an object correctly,
and attesting against the wrong one clears altered objects and condemns sound
ones.
