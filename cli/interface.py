
import sys
import os
import argparse

# Root-Verzeichnis importierbar machen
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.encoder import encode_bytes_to_zw
from core.decoder import decode_zw_to_bytes
from core.crypto import encrypt_payload, decrypt_payload
from cli.injector import inject_payload

def cmd_hide(args):
    with open(args.carrier, "r", encoding="utf-8") as f:
        carrier_text = f.read()

    with open(args.secret, "rb") as f:
        secret_bytes = f.read()

    # Verschlüsseln (falls Passwort angegeben)
    processed_bytes = encrypt_payload(secret_bytes, args.password or "")
    zw_data = encode_bytes_to_zw(processed_bytes)
    result_text = inject_payload(carrier_text, zw_data, mode=args.mode)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result_text)

    print(f"[+] '{args.secret}' ({len(secret_bytes)} Bytes) erfolgreich in '{args.output}' versteckt!")

def cmd_extract(args):
    with open(args.carrier, "r", encoding="utf-8") as f:
        carrier_text = f.read()

    zw_bytes = decode_zw_to_bytes(carrier_text)
    plain_bytes = decrypt_payload(zw_bytes, args.password or "")

    with open(args.output, "wb") as f:
        f.write(plain_bytes)

    print(f"[+] Datei erfolgreich extrahiert: '{args.output}' ({len(plain_bytes)} Bytes)!")

def main():
    parser = argparse.ArgumentParser(description="GhostByte - Invisible Unicode Steganography Storage")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # hide
    hide_p = subparsers.add_parser("hide", help="Versteckt eine Datei in einem Trägertext")
    hide_p.add_argument("carrier", help="Pfad zum Trägertext (.txt)")
    hide_p.add_argument("secret", help="Pfad zur Geheimdatei (beliebig)")
    hide_p.add_argument("output", help="Ausgabedatei")
    hide_p.add_argument("-p", "--password", help="Optionales AES-256 Passwort", default="")
    hide_p.add_argument("-m", "--mode", choices=["paragraph", "spaces"], default="paragraph")

    # extract
    ext_p = subparsers.add_parser("extract", help="Extrahiert eine verborgene Datei aus Trägertext")
    ext_p.add_argument("carrier", help="Pfad zur präparierten Textdatei")
    ext_p.add_argument("output", help="Zielpfad für die extrahierte Datei")
    ext_p.add_argument("-p", "--password", help="AES-256 Passwort (falls verwendet)", default="")

    args = parser.parse_args()
    if args.command == "hide":
        cmd_hide(args)
    elif args.command == "extract":
        cmd_extract(args)

if __name__ == "__main__":
    main()