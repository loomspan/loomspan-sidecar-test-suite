"""One fixed receiver-local post-effect loss instrument; never an open proxy."""

import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import ssl
import sys
import threading
import time


class State:
    def __init__(self, recipe, peer):
        self.recipe, self.peer = recipe, peer
        self.lock = threading.Lock()
        self.counts = {"attempts": 0, "forwards": 0, "accepted": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path != "/counts":
            self.send_error(404)
            return
        with self.server.state.lock:
            body = json.dumps(self.server.state.counts).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        state = self.server.state
        path = (
            "/v1/skills/localEffect/executions"
            if state.peer == "sidecar"
            else "/loomspan/callbacks/owned"
        )
        if self.path != path:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 <= length <= 1024 * 1024:
            self.send_error(413)
            return
        body = self.rfile.read(length)
        with state.lock:
            state.counts["attempts"] += 1
        if state.recipe == "standard":
            context = ssl.create_default_context(cafile="/tls/group-ca.pem")
            connection = http.client.HTTPSConnection(
                state.peer, 8443, context=context, timeout=5
            )
        else:
            connection = http.client.HTTPConnection(
                "127.0.0.1", 8080 if state.peer == "sidecar" else 8081, timeout=5
            )
        try:
            with state.lock:
                state.counts["forwards"] += 1
            connection.request(
                "POST",
                path,
                body,
                {
                    "Authorization": self.headers.get("Authorization", ""),
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            response.read(1024 * 1024)
            if response.status in (200, 202):
                if state.peer == "sidecar":
                    deadline = time.monotonic() + 5
                    while True:
                        control = http.client.HTTPConnection(
                            "127.0.0.1", 8090, timeout=2
                        )
                        control.request("GET", "/status")
                        effects = json.loads(control.getresponse().read())["effects"]
                        control.close()
                        if effects == 1:
                            break
                        assert time.monotonic() < deadline
                        time.sleep(0.05)
                with state.lock:
                    state.counts["accepted"] += 1
        finally:
            connection.close()
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()


def serve(recipe, peer):
    state = State(recipe, peer)
    control = ThreadingHTTPServer(("127.0.0.1", 9082), Handler)
    control.state = state
    threading.Thread(target=control.serve_forever, daemon=True).start()
    server = ThreadingHTTPServer(
        (
            "0.0.0.0" if recipe == "standard" else "127.0.0.1",
            9443 if recipe == "standard" else 9081,
        ),
        Handler,
    )
    server.state = state
    if recipe == "standard":
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            "/tls/" + peer + "-server.pem", "/tls/" + peer + "-server-key.pem"
        )
        server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


if __name__ == "__main__":
    serve(*sys.argv[1:])
