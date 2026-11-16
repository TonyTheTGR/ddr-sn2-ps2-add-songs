"""DDR X read-only backend regression tests."""
import unittest
import ddrx


class DDRXTests(unittest.TestCase):
    def test_archive_list(self):
        self.assertEqual(ddrx.DDRX_ELF, "SLUS_217.67")
        self.assertEqual(ddrx.ARCHIVES[-1], "MDB_X1.DAT")

    def test_slot_pairs(self):
        game = ddrx.Game.__new__(ddrx.Game)
        game.toc = {
            "MUSIC/dace.vig": {}, "SEL/dace_s.vig": {},
            "MUSIC/only.vig": {}, "SEL/else_s.vig": {},
        }
        self.assertEqual(game.slot_codes(), ["dace"])

    def test_readonly_guards(self):
        game = ddrx.Game.__new__(ddrx.Game)
        with self.assertRaises(ddrx.DDRXError):
            game.set_entry("mdb/csq_all.bin", 0, b"test")
        with self.assertRaises(ddrx.DDRXError):
            game.record("dace")

    def test_manifest(self):
        game = ddrx.Game.__new__(ddrx.Game)
        game.elf_name = "SLUS_217.67"
        game.toc = {
            "mdb/csq_all.bin": {"archive": 1, "sector": 3, "size": 100},
            "mdb/music_dt.bin": {"archive": 1, "sector": 5, "size": 200},
            "MUSIC/dace.vig": {"archive": 3},
            "SEL/dace_s.vig": {"archive": 3},
        }
        manifest = game.manifest()
        self.assertEqual(manifest["paired_audio_slots"], 1)
        self.assertEqual(manifest["resources"]["mdb/csq_all.bin"]["archive"], "IMAGE.DAT")


if __name__ == "__main__":
    unittest.main()
