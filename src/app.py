"""Parking-Lot staff login web app.

Single-file application built on the Python standard library only.

Run:
    python src/app.py           # serve on http://127.0.0.1:8000/ until killed
    python src/app.py --port 0  # bind an ephemeral port
    python src/app.py --check   # headless self-check; prints login-ok, exit 0

Default credentials (edit these constants to change them): staff / parking123.
"""

import html
import http.server
import sys
import urllib.parse

HOST = "127.0.0.1"
PORT = 8000
MAX_BODY_SIZE = 8192

STAFF_USERNAME = "staff"
STAFF_PASSWORD = "parking123"


class LoginHandler(http.server.BaseHTTPRequestHandler):
    """Routes requests and writes HTTP responses. Never logs request bodies."""

    server_version = "ParkingLotLogin/1.0"

    def do_GET(self):
        if self.path == "/":
            body = _render_login().encode("utf-8")
        else:
            body = _render_error().encode("utf-8")
        self._send(body)

    def do_POST(self):
        if self.path != "/login":
            self._send(_render_error().encode("utf-8"))
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > MAX_BODY_SIZE:
            self._send(_render_error().encode("utf-8"))
            return
        raw = self.rfile.read(length).decode("utf-8", "replace")
        self._send(_handle_login_post(raw).encode("utf-8"))

    def _send(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _render_login():
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head><meta charset=\"utf-8\"><title>Staff Login</title></head>\n"
        "<body>\n"
        "<h1>Staff Login</h1>\n"
        "<form method=\"post\" action=\"/login\">\n"
        "  <label for=\"username\">Username</label>\n"
        "  <input type=\"text\" id=\"username\" name=\"username\" required>\n"
        "  <label for=\"password\">Password</label>\n"
        "  <input type=\"password\" id=\"password\" name=\"password\" required>\n"
        "  <button type=\"submit\">Log in</button>\n"
        "</form>\n"
        "</body>\n"
        "</html>\n"
    )


def _handle_login_post(body):
    fields = urllib.parse.parse_qs(body, keep_blank_values=False)
    username = fields.get("username", [""])[-1]
    password = fields.get("password", [""])[-1]
    if not username or not password:
        return _render_error()
    if _authenticate(username, password):
        return _render_success(username)
    return _render_error()


def _authenticate(username, password):
    return username == STAFF_USERNAME and password == STAFF_PASSWORD


def _render_success(username):
    safe = html.escape(username)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head><meta charset=\"utf-8\"><title>Login successful</title></head>\n"
        "<body>\n"
        f"<h1>Login successful, welcome {safe}.</h1>\n"
        '<p><a href="/">Back to login</a></p>\n'
        "</body>\n"
        "</html>\n"
    )


def _render_error():
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head><meta charset=\"utf-8\"><title>Login failed</title></head>\n"
        "<body>\n"
        "<h1>Invalid username or password.</h1>\n"
        '<p><a href="/">Back to login</a></p>\n'
        "</body>\n"
        "</html>\n"
    )


def _check():
    """Headless self-check. Prints login-ok and returns 0 on success, else 1."""
    problems = []
    if not isinstance(STAFF_USERNAME, str) or not STAFF_USERNAME:
        problems.append("STAFF_USERNAME missing or empty")
    if not isinstance(STAFF_PASSWORD, str) or not STAFF_PASSWORD:
        problems.append("STAFF_PASSWORD missing or empty")
    if not isinstance(PORT, int) or PORT < 0:
        problems.append("PORT must be a non-negative int")
    if not callable(getattr(LoginHandler, "do_GET", None)):
        problems.append("LoginHandler.do_GET missing")
    if not callable(getattr(LoginHandler, "do_POST", None)):
        problems.append("LoginHandler.do_POST missing")
    if problems:
        for message in problems:
            print(f"check failed: {message}", file=sys.stderr)
        return 1
    print("login-ok")
    return 0


def create_server(host, port):
    """Factory returning a configured HTTPServer (test injection hook)."""
    return http.server.ThreadingHTTPServer((host, port), LoginHandler)


def main(argv):
    if "--check" in argv:
        return _check()
    port = PORT
    if "--port" in argv:
        index = argv.index("--port")
        if index + 1 >= len(argv):
            print("error: --port requires a value", file=sys.stderr)
            return 2
        try:
            port = int(argv[index + 1])
        except ValueError:
            print("error: --port requires an integer", file=sys.stderr)
            return 2
    server = create_server(HOST, port)
    bound = server.server_address[1]
    print(f"Serving on http://{HOST}:{bound}/ ...", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))