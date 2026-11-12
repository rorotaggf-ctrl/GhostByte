import struct
from core.fec import decode_fec

ZW_MAP = {
    '00': '\u200B',
    '01': '\u200C',
    '10': '\u200D',
    '11': '\uFEFF',
}
REV_ZW = {v: k for k, v in ZW_MAP.items()}

MAGIC_START = "\u200B\u200D\u200B\u200D"

def decode_zw_to_bytes(text: str) -> tuple[bytes, dict]:
    start_idx = text.find(MAGIC_START)
    has_header = True

    if start_idx != -1:
        raw_stream = text[start_idx + len(MAGIC_START):]
    else:
        raw_stream = text
        has_header = False

    bit_chunks = []
    for char in raw_stream:
        if char in REV_ZW:
            bit_chunks.append(REV_ZW[char])

    if not bit_chunks:
        raise ValueError("Keine GhostByte-Daten im Text gefunden.")

    bit_string = "".join(bit_chunks)
    usable_bits = (len(bit_string) // 8) * 8
    bit_string = bit_string[:usable_bits]

    all_bytes = bytearray()
    for i in range(0, len(bit_string), 8):
        all_bytes.append(int(bit_string[i:i+8], 2))

    if has_header and len(all_bytes) >= 4:
        expected_len = struct.unpack(">I", bytes(all_bytes[:4]))[0]
        fec_stream = bytes(all_bytes[4:4 + expected_len])
        truncated = len(fec_stream) < expected_len
    else:
        fec_stream = bytes(all_bytes)
        expected_len = len(fec_stream)
        truncated = True

    valid_mask = [True] * len(fec_stream)
    recovered_bytes, repaired = decode_fec(fec_stream, valid_mask)

    stats = {
        "truncated": truncated,
        "repaired_bytes": repaired,
        "found_bytes": len(fec_stream),
        "expected_bytes": expected_len
    }
    return recovered_bytes, stats