from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serveur de keep-alive démarré sur le port {port}")
    server.serve_forever()

def start_keep_alive():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
