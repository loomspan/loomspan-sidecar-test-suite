"""Fixed local OpenAI fixture. No forwarding, request capture or access logging."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPConnection
import json
import socket
import threading


class FixtureServer(ThreadingHTTPServer):
    def __init__(self, address):
        super().__init__(address, Handler)
        self.requests = 0
        self.effects = 0
        self.submissions = 0
        self.forwards = 0
        self.lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/counts":
            with self.server.lock:
                counts = {
                    "modelRequests": self.server.requests,
                    "syntheticEffects": self.server.effects,
                    "submissionAttempts": self.server.submissions,
                    "forwardAttempts": self.server.forwards,
                }
            self.respond(200, counts)
        else:
            self.respond(404, {"error": "unknown endpoint"})

    def do_POST(self):
        if self.path not in ("/v1/chat/completions", "/fail", "/effect"):
            self.respond(404, {"error": "unknown endpoint"})
            return
        # Discard the body without interpreting or retaining it. Bound input size.
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.respond(400, {"error": "invalid length"})
            return
        if not 0 <= length <= 1024 * 1024:
            self.respond(413, {"error": "request too large"})
            return
        self.rfile.read(length)
        if self.path == "/fail":
            self.respond(503, {"error": "fixed SDK fixture failure"})
            return
        if self.path == "/effect":
            with self.server.lock:
                self.server.effects += 1
            self.respond(200, {"effect": "recorded"})
            return
        with self.server.lock:
            self.server.requests += 1
        self.respond(
            200,
            {
                "id": "sdk-fixture",
                "object": "chat.completion",
                "created": 0,
                "model": "sdk-fixture",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "fixture result"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            },
        )


class LossProxy(ThreadingHTTPServer):
    """One fixed submission path and destination, with deliberately lost response."""

    def __init__(self, address, fixture, destination=("sidecar", 8080)):
        super().__init__(address, LossHandler)
        self.fixture = fixture
        self.destination = destination


class LossHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.path != "/v1/skills/sdkEffect/executions":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if not 0 <= length <= 1024 * 1024:
            self.send_error(413)
            return
        body = self.rfile.read(length)
        fixture = self.server.fixture
        with fixture.lock:
            fixture.submissions += 1
            fixture.forwards += 1
        connection = HTTPConnection(*self.server.destination, timeout=10)
        try:
            # HTTPConnection sends once; no redirects, authentication or retry loop.
            connection.request(
                "POST",
                self.path,
                body,
                {
                    "Authorization": self.headers.get("Authorization", ""),
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            response.read(1024 * 1024)
        except (OSError, ValueError):
            pass
        finally:
            connection.close()
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()


if __name__ == "__main__":
    fixture = FixtureServer(("0.0.0.0", 8080))
    proxy = LossProxy(("0.0.0.0", 8081), fixture)
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    fixture.serve_forever()
