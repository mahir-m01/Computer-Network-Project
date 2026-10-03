import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

name = os.environ["BACKEND_ID"]
port = int(os.environ["PORT"])
etag = '"cn-cache-v1"'


class App(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def reply(self, send_body):
        path = self.path.split("?")[0]
        cache = path == "/api/cache"

        if cache and self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("X-Backend", name)
            self.send_header("ETag", etag)
            self.end_headers()
            return

        if path == "/api/status":
            status, data = 200, {"backend": name, "status": "ok"}
        elif cache:
            status, data = 200, {"message": "CN cache example"}
        elif path == "/":
            status, data = 200, {"backend": name}
        else:
            status, data = 404, {"error": "not found"}

        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Backend", name)
        self.send_header("Cache-Control", "public, max-age=60" if cache else "no-store")
        if cache:
            self.send_header("ETag", etag)
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def do_GET(self):
        self.reply(True)

    def do_HEAD(self):
        self.reply(False)


ThreadingHTTPServer(("0.0.0.0", port), App).serve_forever()
