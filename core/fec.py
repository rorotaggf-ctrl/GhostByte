GF_EXP = [0] * 512
GF_LOG = [0] * 256

def _init_gf():
    x = 1
    for i in range(255):
        GF_EXP[i] = x
        GF_LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11d
    for i in range(255, 512):
        GF_EXP[i] = GF_EXP[i - 255]

_init_gf()

def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]

def gf_inv(a: int) -> int:
    return GF_EXP[255 - GF_LOG[a]]

def encode_fec(data: bytes) -> bytes:
    out = bytearray()
    for i in range(0, len(data), 4):
        blk = list(data[i:i+4])
        orig_len = len(blk)
        while len(blk) < 4:
            blk.append(0)
        p0 = blk[0] ^ blk[1] ^ blk[2] ^ blk[3]
        p1 = gf_mul(1, blk[0]) ^ gf_mul(2, blk[1]) ^ gf_mul(4, blk[2]) ^ gf_mul(8, blk[3])
        out.append(orig_len)
        out.extend(blk)
        out.append(p0)
        out.append(p1)
    return bytes(out)

def decode_fec(stream: bytes, valid_mask: list[bool]) -> tuple[bytes, int]:
    recovered = bytearray()
    repaired_bytes = 0
    coeff = [1, 2, 4, 8]

    for i in range(0, len(stream), 7):
        chunk = list(stream[i:i+7])
        mask = valid_mask[i:i+7]
        if len(chunk) < 7:
            orig_len = chunk[0] if mask[0] else max(0, len(chunk) - 1)
            for idx in range(1, min(len(chunk), 1 + orig_len)):
                if mask[idx]:
                    recovered.append(chunk[idx])
            break

        orig_len = chunk[0] if mask[0] else 4
        if orig_len > 4 or orig_len == 0:
            orig_len = 4

        d = chunk[1:5]
        d_ok = mask[1:5]
        p0, p1 = chunk[5], chunk[6]
        p0_ok, p1_ok = mask[5], mask[6]

        missing = [idx for idx, ok in enumerate(d_ok) if not ok]

        if len(missing) == 0:
            if p0_ok and p1_ok:
                s0 = d[0] ^ d[1] ^ d[2] ^ d[3] ^ p0
                s1 = gf_mul(1, d[0]) ^ gf_mul(2, d[1]) ^ gf_mul(4, d[2]) ^ gf_mul(8, d[3]) ^ p1
                if s0 != 0 or s1 != 0:
                    for pos in range(4):
                        if gf_mul(coeff[pos], s0) == s1:
                            d[pos] ^= s0
                            repaired_bytes += 1
                            break
        elif len(missing) == 1 and p0_ok:
            m = missing[0]
            val = p0
            for idx in range(4):
                if idx != m:
                    val ^= d[idx]
            d[m] = val
            repaired_bytes += 1
        elif len(missing) == 1 and p1_ok:
            m = missing[0]
            val = p1
            for idx in range(4):
                if idx != m:
                    val ^= gf_mul(coeff[idx], d[idx])
            d[m] = gf_mul(val, gf_inv(coeff[m]))
            repaired_bytes += 1
        elif len(missing) == 2 and p0_ok and p1_ok:
            m1, m2 = missing[0], missing[1]
            rem0 = p0
            rem1 = p1
            for idx in range(4):
                if idx not in (m1, m2):
                    rem0 ^= d[idx]
                    rem1 ^= gf_mul(coeff[idx], d[idx])
            denom = coeff[m1] ^ coeff[m2]
            x2 = gf_mul(rem1 ^ gf_mul(coeff[m1], rem0), gf_inv(denom))
            x1 = rem0 ^ x2
            d[m1] = x1
            d[m2] = x2
            repaired_bytes += 2

        recovered.extend(d[:orig_len])

    return bytes(recovered), repaired_bytes