"""Parking-lot staff login web app.

A minimal, standard-library-only web app served on 127.0.0.1.

CLI modes:
    python src/app.py          serve until killed (default port 8000)
    python src/app.py --check  validate handlers, print "login-ok", exit 0
"""

import sys
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

ACCEPTED_CREDENTIALS = {
    "staff": "parking123",
}

LOGIN_PAGE = """<!DOCTYPE html>
<html>
<head><title>Staff Login</title></head>
<body>
  <h1>Staff Login</h1>
  <form method="post" action="/">
    <label>Username <input type="text" name="username"></label>
    <label>Password <input type="password" name="password"></label>
    <button type="submit">Log in</button>
  </form>
</body>
</html>
"""

SUCCESS_PAGE = """<!DOCTYPE html>
<html>
<head><title>Login Successful</title></head>
<body>
  <h1>Login successful</h1>
  <p>Welcome, {username}.</p>
</body>
</html>
"""

ERROR_PAGE = """<!DOCTYPE html>
<html>
<head><title>Login Failed</title></head>
<body>
  <h1>Login failed</h1>
  <p>Invalid username or password.</p>
</body>
</html>
"""


class LoginHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        self._respond(200, LOGIN_PAGE)

    def do_POST(self):
        if self.path != "/":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", "replace")
        fields = urllib.parse.parse_qs(body)
        username = fields.get("username", [""])[0]
        password = fields.get("password", [""])[0]
        if ACCEPTED_CREDENTIALS.get(username) == password:
            self._respond(200, SUCCESS_PAGE.format(username=username))
        else:
            self._respond(200, ERROR_PAGE)

    def _respond(self, status, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


def create_server(host="127.0.0.1", port=8000):
    return HTTPServer((host, port), LoginHandler)


def run_check():
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        base = "http://{}:{}".format(host, port)
        with urllib.request.urlopen(base + "/") as response:
            page = response.read().decode("utf-8")
            if response.status != 200 or "Staff Login" not in page:
                return 1
        data = urllib.parse.urlencode(
            {"username": "staff", "password": "parking123"}
        ).encode()
        with urllib.request.urlopen(base + "/", data=data) as response:
            page = response.read().decode("utf-8")
            if response.status != 200 or "Login successful" not in page:
                return 1
        print("login-ok")
        return 0
    finally:
        server.shutdown()
        server.server_close()


def main(argv):
    if "--check" in argv:
        sys.exit(run_check())
    server = create_server()
    print("Serving on 127.0.0.1:8000 (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main(sys.argv[1:])