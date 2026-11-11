import os
import ctypes
import hashlib

lib_path = os.path.join(os.path.dirname(__file__), "libaes.so")
has_c_aes = False

if os.path.exists(lib_path):
    try:
        aes_lib = ctypes.CDLL(lib_path)
        aes_lib.aes256_ctr_crypt.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
            ctypes.c_char_p, ctypes.c_char_p
        ]
        has_c_aes = True
    except Exception:
        pass

def derive_key(passphrase: str) -> bytes:
    # 256-Bit SHA256 Key
    return hashlib.sha256(passphrase.encode("utf-8")).digest()

def encrypt_payload(data: bytes, passphrase: str) -> bytes:
    if not passphrase:
        return data
    key = derive_key(passphrase)
    iv = os.urandom(16)
    
    if has_c_aes:
        out = bytearray(len(data))
        aes_lib.aes256_ctr_crypt(data, (ctypes.c_char * len(data)).from_buffer(out), len(data), key, iv)
        return iv + bytes(out)
    else:
        # Fallback Key-Stream
        keystream = hashlib.sha256(key + iv).digest()
        cipher = bytearray()
        for i, b in enumerate(data):
            cipher.append(b ^ keystream[i % len(keystream)])
        return iv + bytes(cipher)

def decrypt_payload(data: bytes, passphrase: str) -> bytes:
    if not passphrase:
        return data
    iv = data[:16]
    cipher = data[16:]
    key = derive_key(passphrase)

    if has_c_aes:
        out = bytearray(len(cipher))
        aes_lib.aes256_ctr_crypt(cipher, (ctypes.c_char * len(cipher)).from_buffer(out), len(cipher), key, iv)
        return bytes(out)
    else:
        keystream = hashlib.sha256(key + iv).digest()
        plain = bytearray()
        for i, b in enumerate(cipher):
            plain.append(b ^ keystream[i % len(keystream)])
        return bytes(plain)