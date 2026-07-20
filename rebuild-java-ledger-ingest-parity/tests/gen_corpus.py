"""Generate branch ledger corpora.

One generator serves both the shipped sample and the held-out grading corpora, so
they cannot drift apart in shape. Each axis can be switched on independently,
which is how a variant isolates a single quirk.

  python3 tools/gen_corpus.py <out-dir> --profile sample --seed 11
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

ACCOUNTS = ["ACC-1001", "ACC-1002", "ACC-1003", "ACC-2001", "ACC-2002", "ACC-3001"]
PARTIES = ["Alpha Ltd", "Beta Holdings", "Gamma Freight", "Delta Foods", "Orion Supply"]
MEMOS = [
    "monthly rebate", "freight charge", "settlement fee", "cafe supplies",
    "annual licence", "courier costs", "storage rental", "audit retainer",
]


def line(seq: int, account: str, party: str, amount: str, memo: str) -> str:
    return f"{seq}|{account}|{party}|{amount}|{memo}"


def build(out: Path, profile: str, seed: int) -> dict:
    rng = random.Random(seed)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.ldg"):
        stale.unlink()

    # Axis switches. The sample deliberately exposes encoding only.
    duplicates = profile in ("dupes", "combined", "held-out")
    latin1_tail = profile in ("sample", "encoding", "combined", "held-out")
    fold_variants = profile in ("fold", "combined", "held-out")

    seq = 1
    files: dict[str, list[bytes]] = {}
    # The sample must not contain an accidental duplicate group, or the survivor
    # rule becomes visible in the one corpus the solver can read.
    used_keys: set[str] = set()

    def fold(account: str, party: str, memo: str) -> str:
        import re
        import unicodedata
        joined = unicodedata.normalize("NFKC", f"{account} {party} {memo}").lower()
        return re.sub(r"\s+", " ", joined).strip()

    def emit(name: str, text: str, encoding: str = "utf-8") -> None:
        files.setdefault(name, []).append(text.encode(encoding))

    n_files = 4 if profile == "sample" else 6
    for f in range(n_files):
        name = f"branch-{f + 1:02d}.ldg"
        rows = 10 if profile == "sample" else rng.randint(6, 12)
        emit(name, "# branch export\n")
        for _ in range(rows):
            for _attempt in range(200):
                acct = rng.choice(ACCOUNTS)
                party = rng.choice(PARTIES)
                memo = rng.choice(MEMOS)
                if duplicates or fold(acct, party, memo) not in used_keys:
                    break
            else:
                continue
            used_keys.add(fold(acct, party, memo))
            amt = f"{rng.randint(100, 90000) / 100:.2f}"
            emit(name, line(seq, acct, party, amt, memo) + "\n")
            if duplicates and rng.random() < 0.35:
                # Same folded key, different seq. Whether the earlier or later
                # seq survives is the whole question.
                later = seq + rng.randint(1, 40)
                variant_party = party.replace(" ", "  ") if fold_variants else party
                variant_memo = memo.upper() if fold_variants else memo
                emit(name, line(later, acct, variant_party, amt, variant_memo) + "\n")
            seq += 1

    # One file carries a byte that is not valid UTF-8. Because the decode
    # decision is taken over the whole file, this also changes how the valid
    # multi-byte sequences earlier in the same file are read.
    if latin1_tail:
        target = f"branch-{n_files:02d}.ldg"
        files[target].insert(1, line(seq, "ACC-9001", "Zeta Import", "412.55",
                                     "café rebate").encode("utf-8") + b"\n")
        seq += 1
        files[target].append(
            line(seq, "ACC-9002", "Zeta Import", "88.10", "caf\xe9 charge")
            .encode("windows-1252") + b"\n")
        seq += 1

    for name, chunks in files.items():
        (out / name).write_bytes(b"".join(chunks))

    return {"files": len(files), "profile": profile, "seed": seed}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--profile", default="held-out",
                    choices=["sample", "encoding", "dupes", "fold", "combined", "held-out"])
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    info = build(Path(args.out), args.profile, args.seed)
    print(f"wrote {info['files']} files to {args.out} (profile={args.profile}, seed={args.seed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
