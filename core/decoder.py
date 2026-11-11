import struct

ZW_MAP = {
    '00': '\u200B',
    '01': '\u200C',
    '10': '\u200D',
    '11': '\uFEFF',
}
REV_ZW = {v: k for k, v in ZW_MAP.items()}

MAGIC_START = "\u200B\u200D\u200B\u200D"

def decode_zw_to_bytes(text: str) -> bytes:
    start_idx = text.find(MAGIC_START)
    if start_idx == -1:
        raise ValueError("Keine GhostByte-Nutzdaten im Traegertext gefunden!")

    raw_stream = text[start_idx + len(MAGIC_START):]
    
    bit_chunks = []
    for char in raw_stream:
        if char in REV_ZW:
            bit_chunks.append(REV_ZW[char])

    bit_string = "".join(bit_chunks)
    
    # Mindestens 4 Bytes (32 Bits) fuer Laengen-Header noetig
    if len(bit_string) < 32:
        raise ValueError("GhostByte-Header beschaedigt oder unvollstaendig!")

    header_bytes = bytearray()
    for i in range(0, 32, 8):
        header_bytes.append(int(bit_string[i:i+8], 2))
    
    expected_len = struct.unpack(">I", bytes(header_bytes))[0]
    total_bits_needed = 32 + (expected_len * 8)

    if len(bit_string) < total_bits_needed:
        raise ValueError("Bitstream unvollstaendig (Daten abgeschnitten).")

    data_bytes = bytearray()
    for i in range(32, total_bits_needed, 8):
        data_bytes.append(int(bit_string[i:i+8], 2))

    return bytes(data_bytes)