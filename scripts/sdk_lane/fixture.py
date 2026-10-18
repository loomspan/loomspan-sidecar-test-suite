"""Fixed local OpenAI fixture. No forwarding, request capture or access logging."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPConnection
import json
import os
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
        self.entered = threading.Event()
        self.release = threading.Event()
        self.detail = threading.Event()
        self.finished = threading.Event()
        self.planner_step = 0


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
        elif self.path == "/shutdown/status":
            self.respond(
                200,
                {
                    name: getattr(self.server, name).is_set()
                    for name in ("entered", "detail", "finished")
                },
            )
        elif self.path == "/headers":
            self.respond(200, dict(self.headers))
        else:
            self.respond(404, {"error": "unknown endpoint"})

    def do_POST(self):
        if self.path not in (
            "/v1/chat/completions",
            "/fail",
            "/effect",
            "/shutdown/reset",
            "/shutdown/release",
            "/callbacks/identity",
            "/callbacks/detail",
            "/planner/chat/completions",
        ):
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
        if self.path == "/shutdown/reset":
            for event in ("entered", "release", "detail", "finished"):
                getattr(self.server, event).clear()
            self.server.planner_step = 0
            self.respond(200, {})
            return
        if self.path == "/shutdown/release":
            self.server.release.set()
            self.respond(200, {})
            return
        if self.path == "/callbacks/identity":
            self.server.entered.set()
            if not self.server.release.wait(30):
                self.respond(504, {})
                return
            self.respond(200, {"identity": "fixture"})
            return
        if self.path == "/callbacks/detail":
            self.server.detail.set()
            self.respond(200, {"detail": "fixture"})
            return
        if self.path == "/planner/chat/completions":
            responses = [
                {
                    "capabilityName": "shutdownPlanner",
                    "createdAt": "2026-09-14T00:00:00Z",
                    "status": "VALID",
                    "tasks": [
                        {
                            "taskId": name,
                            "title": name,
                            "status": "PENDING",
                            "capabilityName": name + "Leaf",
                            "intent": name,
                            "dependsOn": [] if name == "identity" else ["identity"],
                            "expectedOutputs": [name],
                            "parallelGroup": None,
                            "note": "",
                        }
                        for name in ("identity", "detail")
                    ],
                },
                {
                    "stepAction": "CALL_TOOL",
                    "taskId": "identity",
                    "toolName": "identityLeaf",
                    "toolArguments": {"message": "verify"},
                },
                {
                    "stepAction": "CALL_TOOL",
                    "taskId": "detail",
                    "toolName": "detailLeaf",
                    "toolArguments": {"message": "detail"},
                },
                {"stepAction": "FINAL_RESPONSE", "finalResponse": "shutdown complete"},
            ]
            with self.server.lock:
                index = self.server.planner_step
                self.server.planner_step += 1
            if index >= len(responses):
                self.respond(500, {})
                return
            self.respond(
                200,
                {
                    "id": "shutdown-fixture",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "fixture",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": json.dumps(responses[index]),
                            },
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
            if index == 3:
                self.server.finished.set()
            return
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
    fixture = FixtureServer((os.environ.get("SDK_FIXTURE_BIND", "0.0.0.0"), 8080))
    proxy = LossProxy(("0.0.0.0", 8081), fixture)
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    fixture.serve_forever()
