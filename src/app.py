import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Parking Lot Dashboard</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <main class="card">
        <h1>Parking Lot Dashboard</h1>
        <p class="subtitle">Dashboard is a stub &mdash; out of scope for this slice.</p>
    </main>
</body>
</html>
"""


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_file("index.html")
        elif self.path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(DASHBOARD_HTML.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
        else:
            super().do_GET()

    def serve_file(self, filename):
        try:
            with open(os.path.join(STATIC_DIR, filename), "rb") as f:
                body = f.read()
        except OSError:
            self.send_error(404)
            return
        content_type = "text/html; charset=utf-8"
        if filename.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif filename.endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving parking-lot login page on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
