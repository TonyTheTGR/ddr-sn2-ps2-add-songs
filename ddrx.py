#!/usr/bin/env python3
"""Read-only DDR X (USA) PlayStation 2 archive inspector.

Stage 1 backend: reuses the SuperNOVA 2 file-table reader, but deliberately
disables write operations until the DDR X metadata layout is mapped.

Usage: python ddrx.py inspect path/to/DDR_X_USA.iso [--json inventory.json]
"""
import argparse
import json
import re
from pathlib import Path

import sn2

DDRX_ELF = "SLUS_217.67"
ARCHIVES = ("SYSTEM.DAT", "IMAGE.DAT", "SOUND.DAT", "MDB_X1.DAT")
REQUIRED_RESOURCES = ("mdb/csq_all.bin", "mdb/music_dt.bin")


class DDRXError(sn2.SN2Error):
    pass


class Game(sn2.Game):
    """Read-only DDR X game loader; SN2 song-record patching is not validated."""

    def _finish(self):
        if self.elf_name.upper() != DDRX_ELF:
            raise DDRXError(f"Expected DDR X USA ({DDRX_ELF}), got {self.elf_name!r}")
        self._segments()
        self.toc = self._read_toc()
        self.records = {}  # SN2 heuristic is not valid on DDR X.
        missing = [name for name in REQUIRED_RESOURCES if name not in self.toc]
        if missing:
            raise DDRXError("Missing DDR X resources: " + ", ".join(missing))
        if self.iso:
            for archive in ARCHIVES:
                if "DATA/" + archive not in self.files:
                    raise DDRXError("ISO is missing DATA/" + archive)

    def dat_path(self, entry):
        return self.folder / "DATA" / ARCHIVES[entry["archive"]]

    def dat_lba(self, entry):
        return self.files["DATA/" + ARCHIVES[entry["archive"]]][0]

    def slot_codes(self):
        """Only include slots with both full and preview VIG resources."""
        music = {m.group(1) for name in self.toc
                 if (m := re.fullmatch(r"MUSIC/([a-z0-9]{4,5})\.vig", name))}
        previews = {m.group(1) for name in self.toc
                    if (m := re.fullmatch(r"SEL/([a-z0-9]{4,5})_s\.vig", name))}
        return sorted(music & previews)

    def manifest(self):
        slots = self.slot_codes()
        return {
            "game": "Dance Dance Revolution X (USA)",
            "elf": self.elf_name,
            "archive_files": list(ARCHIVES),
            "table_entries": len(self.toc),
            "paired_audio_slots": len(slots),
            "slot_codes": slots,
            "resources": {
                name: {
                    "archive": ARCHIVES[self.entry(name)["archive"]],
                    "sector": self.entry(name)["sector"],
                    "size": self.entry(name)["size"],
                } for name in REQUIRED_RESOURCES
            },
            "song_metadata_status": "unmapped; editing disabled",
            "shock_arrow_status": "unmapped; editing disabled",
        }

    def set_entry(self, *args, **kwargs):
        raise DDRXError("DDR X writes are disabled until record layout is verified")

    def record(self, *args, **kwargs):
        raise DDRXError("DDR X song metadata record layout is not yet mapped")

    def all_records(self, *args, **kwargs):
        raise DDRXError("DDR X song metadata record layout is not yet mapped")

    def unlock_all(self, *args, **kwargs):
        raise DDRXError("DDR X unlock flags are not mapped")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Inspect a DDR X ISO or extracted disc")
    inspect.add_argument("source", type=Path)
    inspect.add_argument("--json", type=Path, metavar="PATH", help="Write JSON inventory")
    args = parser.parse_args(argv)
    if args.command == "inspect":
        game = Game(args.source)
        info = game.manifest()
        print(json.dumps(info, indent=2))
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
