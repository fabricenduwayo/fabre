"""Build the multi-frame GIF fixture with per-frame encrypted payloads.

Each in-scope frame stores ciphertext in a GIF Application Extension block
labelled MRNR/CRYPTO1. The block payload is:

    <frame_id>|HEX<ciphertext_with_tag>

Run from tools/: python3 gen_gif.py
"""

from __future__ import annotations

import pathlib
import struct

import reference as ref

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "environment" / "fixtures" / "evidence.gif"

# Minimal 1x1 indexed colour frames (palette index 0 = black).
_FRAME_RASTER = bytes([0x00, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00])


def _sub_blocks(data: bytes) -> bytes:
    out = bytearray()
    offset = 0
    while offset < len(data):
        chunk = data[offset : offset + 255]
        out.append(len(chunk))
        out.extend(chunk)
        offset += 255
    out.append(0x00)
    return bytes(out)


def _app_extension(frame_id: str, ciphertext: bytes) -> bytes:
    payload = f"{frame_id}|{ciphertext.hex().upper()}".encode("ascii")
    header = bytes([0x21, 0xFF, 0x0B]) + b"MRNR" + b"CRYPTO1" + b"\x03"
    return header + _sub_blocks(payload)


def _image_descriptor(index: int) -> bytes:
    # Slightly different positions so frames are distinguishable in dumps.
    left = index % 4
    top = index // 4
    return bytes([
        0x2C,
        left, 0x00,
        top, 0x00,
        0x01, 0x00,
        0x01, 0x00,
        0x00,
    ])


def _lzw_image_data(frame_id: str) -> bytes:
    # Smallest valid LZW minimum-code-size 2 image data for a 1x1 raster.
    # Embed a decoy payload string so whole-file regex picks up wrong ciphertext.
    decoy = f"{frame_id}|{'00' * 32}".encode("ascii")
    return bytes([0x02, 0x02, 0x4C, 0x01, 0x00, 0x00]) + decoy


def build_gif() -> bytes:
    parts = bytearray()
    parts.extend(b"GIF89a")
    parts.extend(struct.pack("<HH", 1, 1))  # logical screen
    parts.extend(bytes([0x80, 0x00, 0x00]))  # GCT present
    parts.extend(bytes([0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF]))  # black/white

    all_frames = list(ref.FRAMES) + [ref.DECOY_FRAME]
    for frame in sorted(all_frames, key=lambda f: f["gif_index"]):
        if frame["frame_id"] != ref.DECOY_FRAME["frame_id"]:
            # Superseded capture: valid MRNR/CRYPTO1 block with wrong key material.
            stale_kv = max(1, frame["key_version"] - 1)
            stale_nonce = ref.derived_nonce(frame["frame_id"], stale_kv)
            stale_ct = ref.encrypt_payload(
                frame["frame_id"], frame["plaintext"], stale_kv, stale_nonce
            )
            parts.extend(_app_extension(frame["frame_id"], stale_ct))

        if frame["frame_id"] == ref.DECOY_FRAME["frame_id"]:
            kv = frame["key_version"]
            nonce = ref.derived_nonce(frame["frame_id"], kv)
        else:
            kv = frame["key_version"]
            nonce = ref.operative_nonce(frame)
        ct = ref.encrypt_payload(frame["frame_id"], frame["plaintext"], kv, nonce)
        parts.extend(_app_extension(frame["frame_id"], ct))
        parts.extend(_image_descriptor(frame["gif_index"]))
        parts.extend(_lzw_image_data(frame["frame_id"]))

    parts.append(0x3B)
    return bytes(parts)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = build_gif()
    OUT.write_bytes(data)
    print(f"wrote {OUT} ({len(data):,} bytes)")


if __name__ == "__main__":
    main()
