"""Fixed TLS loss peers for the installed Python reference."""
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import ssl
import sys
from threading import Lock


def serve(mode):
    peer = 'sidecar' if mode == 'submit' else 'app'
    target = '/v1/skills/referencePost/executions' if mode == 'submit' else '/loomspan/callbacks/owned'
    counts = {'attempts': 0, 'forwards': 0, 'accepted': 0}
    lock = Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            if self.path != '/counts':
                self.send_error(404)
                return
            with lock:
                body = json.dumps(counts).encode()
            self.send_response(200)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != target:
                self.send_error(404)
                return
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 <= length <= 1024:
                self.send_error(413)
                return
            body = self.rfile.read(length)
            with lock:
                counts['attempts'] += 1
            if mode == 'wrong-ca':
                self.send_error(500)
                return
            connection = http.client.HTTPSConnection(
                peer, 8443, context=ssl.create_default_context(cafile='/tls/group-ca.pem'), timeout=5,
            )
            try:
                with lock:
                    counts['forwards'] += 1
                connection.request('POST', target, body, {
                    'Authorization': self.headers['Authorization'],
                    'Content-Type': 'application/json',
                    'X-Reference-Marker': self.headers.get('X-Reference-Marker', ''),
                })
                result = connection.getresponse()
                result.read(1024 * 1024)
                if result.status == (202 if mode == 'submit' else 200):
                    with lock:
                        counts['accepted'] += 1
            finally:
                connection.close()
                self.close_connection = True
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.connection.close()

    server = ThreadingHTTPServer(('0.0.0.0', 9444 if mode == 'wrong-ca' else 9443), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    material = f'{peer}-wrong-ca-server' if mode == 'wrong-ca' else f'{peer}-server'
    context.load_cert_chain(f'/tls/{material}.pem', f'/tls/{material}-key.pem')
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


if __name__ == '__main__':
    serve(sys.argv[1])
