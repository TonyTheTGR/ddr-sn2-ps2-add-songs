"""Tests for the DDR X read-only archive format verifier."""
import struct
import unittest
import ddrx_assets as assets


class DDRXAssetTests(unittest.TestCase):
    def test_valid_pack(self):
        data = struct.pack("<III", 12, 15, 18) + b"abc" + b"def" + b"ghi"
        self.assertEqual(assets.split_verified(data, 3), [b"abc", b"def", b"ghi"])

    def test_truncated_pack(self):
        with self.assertRaises(assets.AssetError):
            assets.split_verified(b"abc", 3)

    def test_nonmonotonic_offsets(self):
        data = struct.pack("<III", 12, 15, 14) + b"abcdefghi"
        with self.assertRaises(assets.AssetError):
            assets.split_verified(data, 3)

    def test_invalid_initial_offset(self):
        data = struct.pack("<II", 4, 9) + b"abcdefghi"
        with self.assertRaises(assets.AssetError):
            assets.split_verified(data, 2)


if __name__ == "__main__":
    unittest.main()
