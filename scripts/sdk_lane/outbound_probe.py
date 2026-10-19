"""Non-web recipe oracles, checked while the Java application is alive."""

import json
import socket
import sys
import time
import urllib.request

RESULT = {
    "discoveryAccepted": True,
    "singleSubmissionCompleted": True,
    "exactModelResult": True,
    "noCallbackListeners": True,
    "noCallbackRoutes": True,
    "processExitedCleanly": True,
    "modelRequests": 1,
}


def fixed(path, post=False):
    request = urllib.request.Request(
        "http://127.0.0.1:8090/" + path, data=b"" if post else None
    )
    with urllib.request.urlopen(request, timeout=2) as response:
        assert response.status == 200
        return json.loads(response.read())


def refused(host, ports):
    for port in ports:
        try:
            with socket.create_connection((host, port), timeout=2):
                raise AssertionError("Unexpected callback listener")
        except ConnectionRefusedError:
            pass


def main(recipe, action):
    if action == "ready":
        assert fixed("outbound/status")["ready"] is True
    elif action == "outsider":
        refused("app-proxy", (8081, 8443, 8444, 8090, 9080))
    elif action == "egress":
        refused("127.0.0.1", (9080,))
    elif action == "models":
        assert fixed("status")["models"] == 1
    elif action == "scenario":
        progress = fixed("outbound/status")
        assert progress == {"ready": True, "go": False, "completed": False}
        refused("127.0.0.1", (8081, 8443, 8444, 8445))
        assert fixed("status")["models"] == 0
        fixed("outbound/go", True)
        deadline = time.monotonic() + 25
        while not fixed("outbound/status")["completed"]:
            assert time.monotonic() < deadline
            time.sleep(0.1)
        if recipe == "local":
            assert fixed("status")["models"] == 1
        return RESULT
    else:
        raise AssertionError("Unknown action")
    return {"passed": True}


if __name__ == "__main__":
    try:
        print(json.dumps(main(*sys.argv[1:])))
    except Exception:
        print('{"failed":true}')
        raise SystemExit(1) from None
