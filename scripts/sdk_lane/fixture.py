"""Fixed local OpenAI fixture. No forwarding, request capture or access logging."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading


class FixtureServer(ThreadingHTTPServer):
    def __init__(self, address):
        super().__init__(address, Handler)
        self.requests = 0
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
                count = self.server.requests
            self.respond(200, {"modelRequests": count})
        else:
            self.respond(404, {"error": "unknown endpoint"})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
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


if __name__ == "__main__":
    FixtureServer(("0.0.0.0", 8080)).serve_forever()
