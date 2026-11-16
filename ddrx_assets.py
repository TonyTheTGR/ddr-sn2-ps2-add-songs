#!/usr/bin/env python3
"""Validate extracted DDR X song chart and artwork packs (read-only).

Usage: python ddrx_assets.py csq_all.bin music_dt.bin [--json audit.json]

Both resources must have been extracted from an owned DDR X (USA) disc.
No game files are written or patched.
"""
from __future__ import annotations
import argparse
import json
import struct
from pathlib import Path
import sn2

SONG_COUNT = 77


class AssetError(ValueError):
    pass


def split_verified(data: bytes, count: int = SONG_COUNT) -> list[bytes]:
    """Validate and split a Konami indexed pack without changing bytes."""
    head_len = count * 4
    if len(data) < head_len:
        raise AssetError(f"Pack too small for {count} offsets: {len(data)} bytes")
    offsets = list(struct.unpack_from(f"<{count}I", data))
    if offsets[0] != head_len:
        raise AssetError(f"Expected first offset {head_len}, got {offsets[0]}")
    if any(a >= b for a, b in zip(offsets, offsets[1:])):
        raise AssetError("Pack offsets must increase strictly")
    if offsets[-1] >= len(data):
        raise AssetError("Last pack offset exceeds pack size")
    return [data[a:b] for a, b in zip(offsets, offsets[1:] + [len(data)])]


def validate_ssq(data: bytes) -> dict:
    chunks = sn2.sm2ddr.read_ssq(data)
    if not chunks:
        raise AssetError("No SSQ chunks found")
    return {"uncompressed_size": len(data), "chunk_count": len(chunks)}


def audit_charts(path: Path) -> dict:
    entries = split_verified(path.read_bytes())
    results = []
    for index, item in enumerate(entries):
        try:
            unpacked = sn2.lz_decompress(item)
            detail = validate_ssq(unpacked)
        except Exception as exc:
            raise AssetError(f"Chart pack entry {index} failed: {exc}") from exc
        results.append({"index": index, "packed_size": len(item), **detail})
    return {"entries": len(results), "items": results}


def audit_artwork(path: Path) -> dict:
    entries = split_verified(path.read_bytes())
    results = []
    for index, item in enumerate(entries):
        try:
            if len(item) < 8:
                raise AssetError("Too small for image offset header")
            start, split = struct.unpack_from("<II", item)
            if start != 8 or split <= start or split >= len(item):
                raise AssetError(f"Invalid image offsets: {start}, {split}")
            title = sn2.lz_decompress(item[start:split])
            banner = sn2.lz_decompress(item[split:])
            if not title.startswith(b"TIM2") or not banner.startswith(b"TIM2"):
                raise AssetError("Image did not decompress to TIM2")
        except Exception as exc:
            raise AssetError(f"Artwork pack entry {index} failed: {exc}") from exc
        results.append({"index": index, "packed_size": len(item),
                        "title_tim2_size": len(title), "banner_tim2_size": len(banner)})
    return {"entries": len(results), "items": results}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("charts", type=Path, help="Extracted mdb/csq_all.bin")
    parser.add_argument("artwork", type=Path, help="Extracted mdb/music_dt.bin")
    parser.add_argument("--json", type=Path, help="Optional JSON report destination")
    args = parser.parse_args(argv)
    result = {"game": "DDR X (USA)", "read_only": True,
              "charts": audit_charts(args.charts),
              "artwork": audit_artwork(args.artwork)}
    print("Chart entries verified:", result["charts"]["entries"])
    print("Artwork entries verified:", result["artwork"]["entries"])
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
