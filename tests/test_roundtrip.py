
import unittest
import os
import sys
import hashlib

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.encoder import encode_bytes_to_zw
from core.decoder import decode_zw_to_bytes
from core.crypto import encrypt_payload, decrypt_payload

class TestGhostByteRoundtrip(unittest.TestCase):

    def test_empty_payload(self):
        data = b""
        encoded = encode_bytes_to_zw(data)
        decoded = decode_zw_to_bytes(encoded)
        self.assertEqual(data, decoded)

    def test_binary_random_blob(self):
        # 4 KB Zufallsdaten
        data = os.urandom(4096)
        encoded = encode_bytes_to_zw(data)
        decoded = decode_zw_to_bytes(encoded)
        self.assertEqual(hashlib.sha256(data).digest(), hashlib.sha256(decoded).digest())

    def test_encrypted_roundtrip(self):
        secret = b"HackClub_Crescent_Weird_Storage_2026_TopSecret"
        pwd = "UltraSecurePassword9435"

        encrypted = encrypt_payload(secret, pwd)
        zw = encode_bytes_to_zw(encrypted)

        recovered_enc = decode_zw_to_bytes(zw)
        decrypted = decrypt_payload(recovered_enc, pwd)
        self.assertEqual(secret, decrypted)

if __name__ == "__main__":
    unittest.main()