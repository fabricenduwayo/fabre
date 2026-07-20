"""Build a blob store: content files under a store root plus the seed SQL.

The shipped corpus and every held-out variant come out of this one code path so
they cannot drift apart. The shipped corpus is deliberately degenerate: where an
object has a chunk map it has exactly one chunk, and that chunk is byte for byte
what `blob_path` points at. Nothing an agent can read locally distinguishes the
chunk map from the materialised blob, which is the point.

  python3 tests/corpus.py <store-root> --profile sample
"""

from __future__ import annotations

import argparse
import hashlib
import random
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ALGOS = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}


@dataclass
class Obj:
    """One object. `chunks` is the durable content, in order.

    `blob` is what the materialised copy holds. When it is None the blob file is
    the concatenation of the chunks, which is the agreeing case. When it is set
    the two copies disagree and only one of them is authoritative.
    """

    oid: str
    bucket: str
    chunks: list[bytes]
    algo: str = "sha256"
    blob: bytes | None = None
    declared: str | None = None      # None -> digest of the durable content
    drop_chunk: int | None = None    # ordinal whose file is not written
    drop_blob: bool = False
    no_chunk_map: bool = False       # blob-only object, no rows in object_chunks
    cache: str | None = None
    shuffle_ordinals: bool = False   # insert chunk rows out of ordinal order
    extra: dict = field(default_factory=dict)

    def content(self) -> bytes:
        return b"".join(self.chunks)

    def blob_bytes(self) -> bytes:
        return self.content() if self.blob is None else self.blob

    def declared_digest(self) -> str:
        if self.declared is not None:
            return self.declared
        return ALGOS[self.algo](self.content()).hexdigest()


def body(rng: random.Random, n: int, tag: str) -> bytes:
    """Deterministic filler that is still distinct per object."""
    head = f"--- {tag} ---\n".encode()
    return head + bytes(rng.randrange(32, 127) for _ in range(n))


def sample(rng: random.Random) -> list[Obj]:
    """The corpus that ships in the image.

    Every chunked object has exactly one chunk equal to its blob, so hashing
    `blob_path` and hashing the chunk map give identical answers everywhere.
    The one non-sha256 object is unattestable for a reason that has nothing to
    do with its algorithm, so the algorithm rule leaves no trace here either.
    """
    out: list[Obj] = []
    for i in range(1, 9):
        oid = f"obj-{i:04d}"
        out.append(Obj(oid, "prod", [body(rng, 220 + i * 13, oid)], cache="verified"))

    # Two objects the store already knows are bad: content does not match what
    # was declared at upload.
    out.append(Obj("obj-0009", "prod", [body(rng, 300, "obj-0009")],
                   declared="0" * 64, cache="verified"))
    out.append(Obj("obj-0010", "prod", [body(rng, 180, "obj-0010")],
                   declared="1" * 64, cache="failed"))

    # Blob-only objects: no chunk map at all, so blob_path is genuinely the
    # content for these and reading it is correct.
    out.append(Obj("obj-0011", "archive", [body(rng, 260, "obj-0011")],
                   no_chunk_map=True, cache="verified"))
    out.append(Obj("obj-0012", "archive", [body(rng, 140, "obj-0012")],
                   no_chunk_map=True, cache="verified"))

    # The one non-sha256 row. Its content is gone, so it is unattestable
    # whichever digest rule you apply and the algorithm rule stays hidden.
    out.append(Obj("obj-0013", "archive", [body(rng, 200, "obj-0013")],
                   algo="sha1", drop_chunk=0, drop_blob=True, cache="verified"))

    # Content missing outright.
    out.append(Obj("obj-0014", "prod", [body(rng, 210, "obj-0014")],
                   drop_chunk=0, drop_blob=True, cache="verified"))
    return out


def variant_a(rng: random.Random) -> list[Obj]:
    """Chunk authority: multi-chunk objects whose blob is a stale earlier
    materialisation. Hashing the blob gives a wrong answer for the first time."""
    out = [
        Obj("obj-a001", "prod",
            [body(rng, 190, "a001-p0"), body(rng, 210, "a001-p1"), body(rng, 170, "a001-p2")],
            blob=body(rng, 190, "a001-stale"), cache="verified"),
        Obj("obj-a002", "prod",
            [body(rng, 240, "a002-p0"), body(rng, 160, "a002-p1")],
            blob=body(rng, 240, "a002-stale"), cache="verified"),
        Obj("obj-a003", "prod", [body(rng, 200, "a003")], cache="verified"),
        Obj("obj-a004", "archive", [body(rng, 150, "a004")], no_chunk_map=True, cache="verified"),
    ]
    return out


def variant_b(rng: random.Random) -> list[Obj]:
    """Partial-materialisation authority: the blob copy holds only the first
    chunk of a multi-chunk object, the shape you get when the blob was written
    once and the object later grew. It looks like a complete object and hashes
    to a clean digest, so a blob reader calls it corrupt or, worse, matches it
    against a stale declared digest and calls it intact. The chunk rows are also
    stored out of ordinal order, so reconstruction has to sort by ordinal."""
    b1 = [body(rng, 180, "b001-p0"), body(rng, 190, "b001-p1"), body(rng, 200, "b001-p2")]
    b2 = [body(rng, 160, "b002-p0"), body(rng, 170, "b002-p1")]
    return [
        Obj("obj-b001", "prod", b1, blob=b1[0], shuffle_ordinals=True, cache="verified"),
        Obj("obj-b002", "prod", b2, blob=b2[0], shuffle_ordinals=True, cache="verified"),
        Obj("obj-b003", "prod", [body(rng, 220, "b003")], cache="verified"),
    ]


def variant_c(rng: random.Random) -> list[Obj]:
    """Digest-algorithm discipline: content that genuinely matches a declared
    sha1. Trusting the declared algorithm calls this intact; it is not."""
    return [
        Obj("obj-c001", "prod", [body(rng, 200, "c001")], algo="sha1", cache="verified"),
        Obj("obj-c002", "prod", [body(rng, 180, "c002")], algo="md5", cache="verified"),
        Obj("obj-c003", "prod", [body(rng, 210, "c003")], cache="verified"),
        Obj("obj-c004", "prod", [body(rng, 190, "c004")], declared="2" * 64, cache="verified"),
    ]


def variant_d(rng: random.Random) -> list[Obj]:
    """Bucket discipline: a chunk row pointing at a file that is not there. The
    object is unattestable, not corrupt, and the blob copy does not rescue it."""
    return [
        Obj("obj-d001", "prod",
            [body(rng, 170, "d001-p0"), body(rng, 180, "d001-p1")],
            drop_chunk=1, cache="verified"),
        Obj("obj-d002", "prod",
            [body(rng, 200, "d002-p0"), body(rng, 150, "d002-p1")],
            drop_chunk=0, blob=body(rng, 200, "d002-stale"), cache="verified"),
        Obj("obj-d003", "prod", [body(rng, 190, "d003")], cache="verified"),
    ]


def variant_e(rng: random.Random) -> list[Obj]:
    """Cache conflicts driven by chunk authority. The conflict set is not the
    cache read back verbatim: it is the disagreement between the cache and what
    the durable content actually hashes to, so getting it right needs the chunk
    map, not the blob."""
    e2_stale = body(rng, 180, "e002-stale")
    return [
        # Blob is stale but the chunks are the declared content: really intact
        # with no conflict. Hashing the blob invents a corrupt verdict and a
        # spurious conflict.
        Obj("obj-e001", "prod",
            [body(rng, 190, "e001-p0"), body(rng, 200, "e001-p1")],
            blob=body(rng, 190, "e001-stale"), cache="verified"),
        # Declared matches the stale blob, so hashing the blob calls it intact
        # and finds no conflict. The chunks hash to something else, so it is
        # corrupt and the verified cache row is a genuine conflict.
        Obj("obj-e002", "prod",
            [e2_stale, body(rng, 170, "e002-p1")],
            blob=e2_stale, declared=hashlib.sha256(e2_stale).hexdigest(),
            cache="verified"),
        # Cache says failed but the content is genuinely intact: a conflict in
        # the other direction that both routes should catch.
        Obj("obj-e003", "prod", [body(rng, 210, "e003")], cache="failed"),
        Obj("obj-e004", "prod", [body(rng, 160, "e004")], cache=None),
    ]


def variant_f(rng: random.Random) -> list[Obj]:
    """The combined case. Multi-chunk with a stale blob, declared under sha1,
    carrying a verified cache row, and the stale blob's sha1 matches what was
    declared. Every wrong route agrees with itself and says intact."""
    stale = body(rng, 200, "f001-stale")
    out = [
        Obj("obj-f001", "prod",
            [stale, body(rng, 190, "f001-p1"), body(rng, 175, "f001-p2")],
            algo="sha1", blob=stale,
            declared=hashlib.sha1(stale).hexdigest(), cache="verified"),
        Obj("obj-f002", "prod",
            [body(rng, 180, "f002-p0"), body(rng, 200, "f002-p1")],
            blob=body(rng, 180, "f002-stale"), shuffle_ordinals=True, cache="verified"),
        Obj("obj-f003", "prod", [body(rng, 210, "f003")], drop_chunk=0, cache="verified"),
        Obj("obj-f004", "prod", [body(rng, 190, "f004")], cache="verified"),
    ]
    return out


PROFILES = {
    "sample": sample,
    "variant-a": variant_a,
    "variant-b": variant_b,
    "variant-c": variant_c,
    "variant-d": variant_d,
    "variant-e": variant_e,
    "variant-f": variant_f,
}


def sql_str(value) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def build(root: Path, profile: str, seed: int) -> tuple[list[Obj], Path]:
    rng = random.Random(seed)
    objects = PROFILES[profile](rng)

    if root.exists():
        shutil.rmtree(root)
    (root / "blobs").mkdir(parents=True)
    (root / "chunks").mkdir(parents=True)

    lines = ["-- generated by tests/corpus.py; do not edit by hand", ""]
    chunk_rows: list[str] = []
    cache_rows: list[str] = []

    for index, obj in enumerate(objects):
        # The row always names a blob file. When drop_blob is set the file is
        # not written, so the pointer dangles — the auditor has to treat a
        # missing materialisation as unreadable rather than trusting the row.
        blob_rel = f"blobs/{obj.oid}.bin"
        if not obj.drop_blob:
            (root / blob_rel).write_bytes(obj.blob_bytes())

        stamp = f"2026-0{1 + index % 9}-1{index % 9} 0{index % 9}:15:00"
        lines.append(
            "INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, "
            "blob_path, size_bytes, created_at) VALUES ("
            f"{sql_str(obj.oid)}, {sql_str(obj.bucket)}, {sql_str(obj.declared_digest())}, "
            f"{sql_str(obj.algo)}, {sql_str(blob_rel)}, {len(obj.content())}, "
            f"{sql_str(stamp)});"
        )

        if not obj.no_chunk_map:
            order = list(range(len(obj.chunks)))
            if obj.shuffle_ordinals:
                order = list(reversed(order))
            for ordinal in order:
                chunk = obj.chunks[ordinal]
                rel = f"chunks/{obj.oid}.{ordinal:03d}"
                if obj.drop_chunk != ordinal:
                    (root / rel).write_bytes(chunk)
                chunk_rows.append(
                    "INSERT INTO object_chunks (object_id, ordinal, chunk_path, size_bytes) "
                    f"VALUES ({sql_str(obj.oid)}, {ordinal}, {sql_str(rel)}, {len(chunk)});"
                )

        if obj.cache:
            digest = obj.declared_digest() if obj.cache == "verified" else None
            cache_rows.append(
                "INSERT INTO attestation_cache (object_id, status, digest, verified_at) "
                f"VALUES ({sql_str(obj.oid)}, {sql_str(obj.cache)}, {sql_str(digest)}, "
                f"{sql_str(stamp)});"
            )

    lines += ["", *chunk_rows, "", *cache_rows, ""]
    seed_sql = root / "seed.sql"
    seed_sql.write_text("\n".join(lines), encoding="utf-8")
    return objects, seed_sql


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--profile", default="sample", choices=sorted(PROFILES))
    ap.add_argument("--seed", type=int, default=20260720)
    args = ap.parse_args()
    objects, seed_sql = build(Path(args.root), args.profile, args.seed)
    chunked = sum(1 for o in objects if not o.no_chunk_map)
    multi = sum(1 for o in objects if not o.no_chunk_map and len(o.chunks) > 1)
    disagree = sum(1 for o in objects if o.blob is not None)
    print(f"profile={args.profile} objects={len(objects)} chunked={chunked} "
          f"multi_chunk={multi} blob_disagrees={disagree} -> {seed_sql}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
