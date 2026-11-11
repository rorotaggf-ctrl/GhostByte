import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from email.message import EmailMessage

# Projektwurzel in den Suchpfad aufnehmen, damit 'core' ueberall gefunden wird
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Direkter Import aus deinen dezentralen Core-Modulen
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
        if self.path == "/api/hide":
            content_type = self.headers.get("Content-Type", "")
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length)

            msg = EmailMessage()
            msg["Content-Type"] = content_type
            msg.set_payload(raw_body)

            carrier = ""
            passphrase = ""
            file_bytes = b""

            for part in msg.iter_parts():
                disp = part.get("Content-Disposition", "")
                if 'name="carrier"' in disp:
                    carrier = part.get_content()
                    if isinstance(carrier, bytes):
                        carrier = carrier.decode("utf-8", errors="replace")
                elif 'name="password"' in disp:
                    passphrase = part.get_content()
                    if isinstance(passphrase, bytes):
                        passphrase = passphrase.decode("utf-8", errors="replace")
                elif 'name="file"' in disp:
                    file_bytes = part.get_payload(decode=True) or b""

            encrypted = encrypt_payload(file_bytes, passphrase)
            zw_encoded = encode_bytes_to_zw(encrypted)
            
            if carrier.strip():
                stego_text = carrier + "\n\n" + zw_encoded
            else:
                stego_text = zw_encoded

            resp = {"success": True, "stego_text": stego_text}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif self.path == "/api/extract":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))

            stego_text = data.get("stego_text", "")
            passphrase = data.get("password", "")

            try:
                raw_bytes = decode_zw_to_bytes(stego_text)
                decrypted = decrypt_payload(raw_bytes, passphrase)

                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", 'attachment; filename="recovered_payload.bin"')
                self.end_headers()
                self.wfile.write(decrypted)
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def run():
    server = HTTPServer(("0.0.0.0", PORT), GhostByteHandler)
    print(f"[*] GhostByte 1995 Webserver lauscht auf http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeende Server...")

if __name__ == "__main__":
    run()