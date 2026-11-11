
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.decoder import ZW_MAP, MAGIC_START, MAGIC_END

COLOR_MAP = {
    '\u200B': '\033[91m[ZWSP]\033[0m',   # Rot
    '\u200C': '\033[92m[ZWNJ]\033[0m',   # Grün
    '\u200D': '\033[93m[ZWJ]\033[0m',    # Gelb
    '\uFEFF': '\033[94m[BOM]\033[0m',    # Blau
}

def inspect_file(filepath: str):
    if not os.path.exists(filepath):
        print(f"[-] Datei nicht gefunden: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    zw_counts = {k: 0 for k in COLOR_MAP}
    for char in content:
        if char in zw_counts:
            zw_counts[char] += 1

    total_zw = sum(zw_counts.values())
    visible_chars = len(content) - total_zw
    approx_payload_bytes = (total_zw - 8) // 4 if total_zw >= 8 else 0

    print("==================================================")
    print(f" GHOSTBYTE INSPECTOR: {os.path.basename(filepath)}")
    print("==================================================")
    print(f" Gesamtlänge Zeichen:  {len(content)}")
    print(f" Sichtbare Zeichen:    {visible_chars}")
    print(f" Unsichtbare Steuerz.: {total_zw}")
    print(f" Geschätzte Nutzlast:  ~{approx_payload_bytes} Bytes")
    print("--------------------------------------------------")
    print(" Aufschlüsselung der Homoglyphen:")
    for k, name in [('\u200B', 'Zero-Width Space (00)'),
                    ('\u200C', 'Zero-Width Non-Joiner (01)'),
                    ('\u200D', 'Zero-Width Joiner (10)'),
                    ('\uFEFF', 'Zero-Width No-Break (11)')]:
        print(f"  {k} {name:28}: {zw_counts[k]}")
    print("==================================================")

    # Terminal-Visualisierung (Ausschnitt)
    print("\nVisualisierungs-Preview (Erste 300 Zeichen gerendert):")
    rendered = []
    for ch in content[:300]:
        if ch in COLOR_MAP:
            rendered.append(COLOR_MAP[ch])
        else:
            rendered.append(ch)
    print("".join(rendered))
    print("\n==================================================")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analysis/inspect.py <datei.txt>")
        sys.exit(1)
    inspect_file(sys.argv[1])