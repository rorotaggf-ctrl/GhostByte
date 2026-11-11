import struct

ZW_MAP = {
    '00': '\u200B',
    '01': '\u200C',
    '10': '\u200D',
    '11': '\uFEFF',
}

MAGIC_START = "\u200B\u200D\u200B\u200D"

def encode_bytes_to_zw(data: bytes) -> str:
    # 4 Bytes Laenge voranstellen
    header = struct.pack(">I", len(data))
    payload = header + data
    
    zw_chunks = []
    for byte in payload:
        bits = f"{byte:08b}"
        zw_chunks.append(ZW_MAP[bits[0:2]])
        zw_chunks.append(ZW_MAP[bits[2:4]])
        zw_chunks.append(ZW_MAP[bits[4:6]])
        zw_chunks.append(ZW_MAP[bits[6:8]])
    return MAGIC_START + "".join(zw_chunks)