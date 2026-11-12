import sys
import os
import json
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.crypto import encrypt_payload, decrypt_payload
from core.encoder import encode_bytes_to_zw
from core.decoder import decode_zw_to_bytes

PORT = 9435

class GhostByteHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            idx_path = os.path.join(os.path.dirname(__file__), "index.html")
            with open(idx_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        if self.path == "/api/hide":
            try:
                data = json.loads(raw_body.decode("utf-8"))
                carrier = data.get("carrier", "")
                secret = data.get("secret", "")
                passphrase = data.get("password", "")

                secret_bytes = secret.encode("utf-8")
                encrypted = encrypt_payload(secret_bytes, passphrase)
                zw_encoded = encode_bytes_to_zw(encrypted)

                # Trennung: Trägertext + versteckte Sequenz
                if carrier.strip():
                    stego_text = carrier + "\n\n" + zw_encoded
                else:
                    stego_text = zw_encoded

                resp = {
                    "success": True,
                    "stego_text": stego_text,
                    "bytes_hidden": len(secret_bytes),
                    "zw_chars": len(zw_encoded)
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == "/api/extract":
            try:
                data = json.loads(raw_body.decode("utf-8"))
                stego_text = data.get("stego_text", "")
                passphrase = data.get("password", "")

                raw_bytes, stats = decode_zw_to_bytes(stego_text)
                decrypted = decrypt_payload(raw_bytes, passphrase)
                extracted_str = decrypted.decode("utf-8", errors="replace")

                resp = {
                    "success": True,
                    "secret": extracted_str,
                    "truncated": stats["truncated"],
                    "repaired_bytes": stats["repaired_bytes"]
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def get_watched_files():
    tracked = []
    for root, _, files in os.walk(ROOT_DIR):
        if ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith((".py", ".html", ".c", ".txt")):
                tracked.append(os.path.join(root, file))
    return tracked

def file_watcher():
    last_mtimes = {f: os.stat(f).st_mtime for f in get_watched_files() if os.path.exists(f)}
    while True:
        time.sleep(1)
        current_files = get_watched_files()
        reboot = False
        for f in current_files:
            try:
                mtime = os.stat(f).st_mtime
                if f not in last_mtimes or mtime > last_mtimes[f]:
                    reboot = True
                    break
            except OSError:
                continue

        if reboot:
            print("\n[!] Aenderung erkannt. Starte Server automatisch neu...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

def run():
    watcher_thread = threading.Thread(target=file_watcher, daemon=True)
    watcher_thread.start()

    server = HTTPServer(("0.0.0.0", PORT), GhostByteHandler)
    print(f"[*] GhostByte Server lauscht auf http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeende Server...")

if __name__ == "__main__":
    run()