"""Build a blob store: content files under a store root plus the seed SQL.

The shipped store and every held-out variant come out of this one code path so
they cannot drift apart. An object declares a byte length and a digest; the store
keeps its bytes as a chunk map and/or a materialised blob, and either copy can be
tampered with or lost while the declaration stands. The shipped store is
degenerate: for every object the chunk map and the blob agree and both match the
declared length, so an auditor that trusts whichever copy is handy reproduces the
correct report on everything the agent can see. The held-out stores are where the
copies disagree.

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
    """One object.

    `declared` is the content the object was declared with; `size_bytes` and
    `declared_digest` describe it. `chunks` and `blob` are what storage actually
    holds and may differ from `declared`. `chunks` is None when the object has
    no chunk rows; `blob` is None when no blob file is written. Each ordinal in
    `drop_chunks` still gets a chunk row but no file on disk, and `drop_blob`
    records a `blob_path` with no file behind it, so that representation is
    unreadable.
    """

    oid: str
    bucket: str
    declared: bytes
    chunks: list[bytes] | None = None
    superseded: list[bytes] | None = None
    blob: bytes | None = None
    algo: str = "sha256"
    declared_digest: str | None = None
    size_bytes: int | None = None
    drop_chunks: list[int] = field(default_factory=list)
    drop_blob: bool = False
    blob_path_null: bool = False
    cache: str | None = None

    def size(self) -> int:
        return self.size_bytes if self.size_bytes is not None else len(self.declared)

    def digest(self) -> str:
        if self.declared_digest is not None:
            return self.declared_digest
        return ALGOS[self.algo](self.declared).hexdigest()


def body(rng: random.Random, n: int, tag: str) -> bytes:
    head = f"--- {tag} ---\n".encode()
    return head + bytes(rng.randrange(32, 127) for _ in range(max(0, n - len(head))))


def sound(rng: random.Random, oid: str, n: int) -> Obj:
    """An object whose chunk map and blob both hold the declared content."""
    content = body(rng, n, oid)
    return Obj(oid, "prod", content, chunks=[content], blob=content, cache="verified")


def sample(rng: random.Random) -> list[Obj]:
    """The shipped store. Every object's two copies agree and match the declared
    length, so no held-out disagreement is visible here."""
    out = [sound(rng, f"obj-{i:04d}", 200 + i * 11) for i in range(1, 9)]

    # Multi-chunk sound objects, blob equal to the whole content.
    for i in (5, 6):
        oid = f"obj-{i:04d}"
        parts = [body(rng, 120, f"{oid}-p0"), body(rng, 130, f"{oid}-p1")]
        content = b"".join(parts)
        out[i - 1] = Obj(oid, "prod", content, chunks=parts, blob=content, cache="verified")

    # Two objects the store already knows are bad: content does not match what
    # was declared. Both copies still match the declared length.
    c9 = body(rng, 300, "obj-0009")
    out.append(Obj("obj-0009", "prod", c9, chunks=[c9], blob=c9,
                   declared_digest="0" * 64, cache="verified"))
    c10 = body(rng, 180, "obj-0010")
    out.append(Obj("obj-0010", "prod", c10, chunks=[c10], blob=c10,
                   declared_digest="1" * 64, cache="failed"))

    # Blob-only objects: no chunk rows, the blob is the content.
    b11 = body(rng, 260, "obj-0011")
    out.append(Obj("obj-0011", "archive", b11, chunks=None, blob=b11, cache="verified"))
    b12 = body(rng, 150, "obj-0012")
    out.append(Obj("obj-0012", "archive", b12, chunks=None, blob=b12, cache="verified"))

    # Content gone from both copies.
    c13 = body(rng, 210, "obj-0013")
    out.append(Obj("obj-0013", "archive", c13, chunks=[c13], blob=c13,
                   drop_chunks=[0], drop_blob=True, cache="verified"))
    c14 = body(rng, 200, "obj-0014")
    out.append(Obj("obj-0014", "prod", c14, chunks=[c14], blob=c14,
                   drop_chunks=[0], drop_blob=True, cache="failed"))
    return out


def variant_a(rng: random.Random) -> list[Obj]:
    """Stale blob, chunk map holds the content: intact on the chunk map, so
    hashing the blob calls a sound object corrupt."""
    out = []
    for oid, n in [("obj-a001", 380), ("obj-a002", 300)]:
        content = body(rng, n, oid)
        stale = body(rng, n - 60, f"{oid}-stale")
        out.append(Obj(oid, "prod", content, chunks=[content], blob=stale, cache="verified"))
    out.append(sound(rng, "obj-a003", 220))
    b4 = body(rng, 240, "obj-a004")
    out.append(Obj("obj-a004", "archive", b4, chunks=None, blob=b4, cache="verified"))
    # Blob-only object whose blob is a stale materialisation: the only copy reads
    # back at the wrong length, so nothing at the declared length is left to
    # attest and the object is unattestable, not corrupt.
    a5 = body(rng, 230, "obj-a005")
    out.append(Obj("obj-a005", "archive", a5, chunks=None, blob=body(rng, 170, "a005-stale"),
                   cache="verified"))
    return out


def variant_b(rng: random.Random) -> list[Obj]:
    """Superseded chunk generations. Re-materialising an object appended a new
    generation of chunk rows and left the older rows in place, so only the latest
    generation is the object's current content. An auditor that reads every chunk
    row, or the wrong generation, reconstructs stale content and calls a sound
    object corrupt; here the blob is stale too, so the current generation is the
    only copy that holds the declared content."""
    out = []
    for oid, n in [("obj-b001", 340), ("obj-b002", 260)]:
        content = body(rng, n, oid)
        old = body(rng, n - 40, f"{oid}-old")
        out.append(Obj(oid, "prod", content, chunks=[content], superseded=[old],
                       blob=body(rng, n - 90, f"{oid}-stale"), cache="verified"))
    out.append(sound(rng, "obj-b003", 210))
    return out


def variant_c(rng: random.Random) -> list[Obj]:
    """Content declared under sha1 or md5. It matches the declared length and
    the declared digest, but the store does not accept the algorithm, so it is
    unattestable rather than intact."""
    out = []
    for oid, algo, n in [("obj-c001", "sha1", 200), ("obj-c002", "md5", 180)]:
        content = body(rng, n, oid)
        out.append(Obj(oid, "prod", content, chunks=[content], blob=content,
                       algo=algo, cache="verified"))
    out.append(sound(rng, "obj-c003", 210))
    c4 = body(rng, 190, "obj-c004")
    out.append(Obj("obj-c004", "prod", c4, chunks=[c4], blob=c4,
                   declared_digest="2" * 64, cache="verified"))
    return out


def variant_d(rng: random.Random) -> list[Obj]:
    """A missing chunk file does not by itself condemn an object. When the blob
    still holds the declared content the object is intact through the blob; only
    when no readable copy matches the declared length is it unattestable."""
    out = []
    # Chunk file gone, blob holds the content: intact through the blob.
    d1 = body(rng, 300, "obj-d001")
    out.append(Obj("obj-d001", "prod", d1, chunks=[d1[:150], d1[150:]], blob=d1,
                   drop_chunks=[1], cache="verified"))
    # Chunk file gone and the blob is stale: no copy matches, unattestable.
    d2 = body(rng, 260, "obj-d002")
    out.append(Obj("obj-d002", "prod", d2,
                   chunks=[body(rng, 130, "d002-p0"), body(rng, 130, "d002-p1")],
                   blob=body(rng, 200, "d002-stale"), drop_chunks=[0], cache="verified"))
    # Both copies gone.
    d3 = body(rng, 190, "obj-d003")
    out.append(Obj("obj-d003", "prod", d3, chunks=[d3], blob=d3,
                   drop_chunks=[0], drop_blob=True, cache="verified"))
    out.append(sound(rng, "obj-d004", 220))
    return out


def variant_e(rng: random.Random) -> list[Obj]:
    """Cache disagreements in both directions, driven by what the copies hash to
    rather than by what the cache says."""
    out = []
    # Stale blob, sound chunk map: intact, verified cache agrees, no conflict.
    e1 = body(rng, 320, "obj-e001")
    out.append(Obj("obj-e001", "prod", e1, chunks=[e1], blob=body(rng, 200, "e001-stale"),
                   cache="verified"))
    # Content matches the declared length but not the declared digest: corrupt,
    # and the verified cache row is a conflict.
    e2 = body(rng, 240, "obj-e002")
    out.append(Obj("obj-e002", "prod", e2, chunks=[e2], blob=e2,
                   declared_digest="3" * 64, cache="verified"))
    # Intact but the cache says failed: a conflict in the other direction.
    e3 = body(rng, 210, "obj-e003")
    out.append(Obj("obj-e003", "prod", e3, chunks=[e3], blob=e3, cache="failed"))
    e4 = body(rng, 160, "obj-e004")
    out.append(Obj("obj-e004", "prod", e4, chunks=[e4], blob=e4, cache=None))
    return out


def variant_f(rng: random.Random) -> list[Obj]:
    """Every axis at once. A stale chunk map with a content-bearing blob that is
    declared under sha1, so the copy that matches the declared length is exactly
    the one the store cannot vouch for, and a verified cache row on top."""
    out = []
    f1 = body(rng, 300, "obj-f001")
    out.append(Obj("obj-f001", "prod", f1, chunks=[body(rng, 200, "f001-stale")], blob=f1,
                   algo="sha1", cache="verified"))
    # Missing chunk rescued by the blob.
    f2 = body(rng, 260, "obj-f002")
    out.append(Obj("obj-f002", "prod", f2,
                   chunks=[body(rng, 130, "f002-p0"), body(rng, 130, "f002-p1")],
                   blob=f2, drop_chunks=[0], cache="verified"))
    # Sound chunk map, stale blob.
    f3 = body(rng, 220, "obj-f003")
    out.append(Obj("obj-f003", "prod", f3, chunks=[f3], blob=body(rng, 150, "f003-stale"),
                   cache="verified"))
    # Both copies gone.
    f4 = body(rng, 200, "obj-f004")
    out.append(Obj("obj-f004", "prod", f4, chunks=[f4], blob=f4,
                   drop_chunks=[0], drop_blob=True, cache="verified"))
    # Declared under sha1 with neither copy at the declared length: unattestable
    # for the missing content, which is decided before the algorithm is weighed.
    f5 = body(rng, 240, "obj-f005")
    out.append(Obj("obj-f005", "prod", f5, chunks=[body(rng, 150, "f005-stale")],
                   blob=body(rng, 150, "f005-blob-stale"), algo="sha1", cache="verified"))
    # Superseded generation whose current chunks hold the content, with a stale
    # blob: sound only if the latest generation is the one that is read.
    f6 = body(rng, 300, "obj-f006")
    out.append(Obj("obj-f006", "prod", f6, chunks=[f6], superseded=[body(rng, 260, "f006-old")],
                   blob=body(rng, 210, "f006-stale"), cache="verified"))
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
        blob_rel = None
        if not obj.blob_path_null:
            blob_rel = f"blobs/{obj.oid}.bin"
            if obj.blob is not None and not obj.drop_blob:
                (root / blob_rel).write_bytes(obj.blob)

        stamp = f"2026-0{1 + index % 9}-1{index % 9} 0{index % 9}:15:00"
        lines.append(
            "INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, "
            "blob_path, size_bytes, created_at) VALUES ("
            f"{sql_str(obj.oid)}, {sql_str(obj.bucket)}, {sql_str(obj.digest())}, "
            f"{sql_str(obj.algo)}, {sql_str(blob_rel)}, {obj.size()}, {sql_str(stamp)});"
        )

        if obj.chunks is not None:
            current_gen = 1 if obj.superseded is not None else 0

            def emit(gen: int, parts: list[bytes]) -> None:
                for ordinal, chunk in enumerate(parts):
                    rel = f"chunks/{obj.oid}.g{gen}.{ordinal:03d}"
                    if not (gen == current_gen and ordinal in obj.drop_chunks):
                        (root / rel).write_bytes(chunk)
                    chunk_rows.append(
                        "INSERT INTO object_chunks "
                        "(object_id, generation, ordinal, chunk_path, size_bytes) "
                        f"VALUES ({sql_str(obj.oid)}, {gen}, {ordinal}, {sql_str(rel)}, "
                        f"{len(chunk)});"
                    )

            if obj.superseded is not None:
                emit(0, obj.superseded)
            emit(current_gen, obj.chunks)

        if obj.cache:
            digest = obj.digest() if obj.cache == "verified" else None
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
    print(f"profile={args.profile} objects={len(objects)} -> {seed_sql}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
