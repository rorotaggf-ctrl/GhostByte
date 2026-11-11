import unittest
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.encoder import encode_bytes_to_zw
from core.decoder import decode_zw_to_bytes

class TestCorruption(unittest.TestCase):

    def test_missing_start_marker(self):
        raw = b"Sample Payload"
        zw = encode_bytes_to_zw(raw)
        corrupted = zw[4:]
        with self.assertRaises(ValueError):
            decode_zw_to_bytes(corrupted)

    def test_truncated_stream(self):
        raw = b"Sample Payload"
        zw = encode_bytes_to_zw(raw)
        # Die letzten 4 Zeichen (1 Byte) abschneiden
        corrupted = zw[:-4]
        with self.assertRaises(ValueError):
            decode_zw_to_bytes(corrupted)

if __name__ == "__main__":
    unittest.main()