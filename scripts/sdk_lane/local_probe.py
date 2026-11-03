"""Bounded fixed Local scenarios, executed inside the shared loopback namespace.

Only booleans, counters and status values leave this process. Session state and
CSRF tokens stay in memory; execution credentials stay in the capture fixture.
"""

import http.cookiejar
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def request(opener, url, data=None, headers=None):
    body = None if data is None else urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers or {})
    try:
        with opener.open(req, timeout=3) as response:
            return response.status, response.read(1024 * 1024)
    except urllib.error.HTTPError as response:
        return response.code, response.read(1024 * 1024)


def fresh():
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    )


def fixed(path, post=False):
    status, body = request(
        fresh(), "http://127.0.0.1:8090" + path, {} if post else None
    )
    assert status == 200
    return json.loads(body)


def login(user="alice"):
    opener = fresh()
    status, body = request(opener, "http://127.0.0.1:8081/login")
    assert status == 200
    token = re.search(r'name="_csrf"[^>]*value="([^"]+)"', body.decode()).group(1)
    request(
        opener,
        "http://127.0.0.1:8081/login",
        {"username": user, "password": "fixture", "_csrf": token},
    )
    status, body = request(opener, "http://127.0.0.1:8081/csrf")
    assert status == 200
    csrf = json.loads(body)
    return opener, {csrf["header"]: csrf["token"]}


def app(session, path, post=False, expected=200):
    opener, headers = session
    status, body = request(
        opener, "http://127.0.0.1:8081" + path, {} if post else None, headers
    )
    assert status == expected
    return json.loads(body) if body else None


def until(action, predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while True:
        value = action()
        if predicate(value):
            return value
        assert time.monotonic() < deadline
        time.sleep(0.1)


def terminal(session, execution):
    return until(
        lambda: app(session, "/executions/" + execution),
        lambda value: value["status"] in ("COMPLETED", "FAILED"),
        20,
    )


def issuance():
    anonymous = fresh()
    status, body = request(anonymous, "http://127.0.0.1:8081/skills")
    assert status == 200 and b'name="username"' in body
    alice = login()
    assert request(alice[0], "http://127.0.0.1:8081/submit/localModel", {})[0] == 403
    execution = app(alice, "/submit/localModel", True)["id"]
    done = terminal(alice, execution)
    assert done == {"status": "COMPLETED", "result": "fixture result", "failure": ""}
    before = fixed("/status")
    app(login("literal"), "/submit/localModel", True, 403)
    assert fixed("/status") == before
    app(login("bob"), "/executions/" + execution, expected=404)
    assert app(login(), "/executions/" + execution)["status"] == "COMPLETED"
    app(alice, "/capture", True)
    assert fixed("/probe")["status"] == 200
    return {
        "formLogin": True,
        "csrf": True,
        "exactRoles": True,
        "ownerFreshRead": True,
        "differentOwner404": True,
    }


def restart():
    # Captured credential predates app restart and has a five-minute lifetime.
    until(lambda: fixed("/probe")["status"], lambda value: value == 401)
    session = login()
    assert app(session, "/skills")["accepted"]
    app(session, "/capture", True)
    assert fixed("/probe")["status"] == 200
    return {"oldRejected": True, "newAccepted": True}


def health():
    status, body = request(fresh(), "http://127.0.0.1:8080/actuator/health/readiness")
    assert status in (200, 503)
    assert json.loads(body) == {"status": "UP" if status == 200 else "DOWN"}
    return status


def trust():
    path = Path("/keys/jwks.json")
    public = path.read_bytes()
    temporary = path.with_name("correction.tmp")
    try:
        temporary.write_bytes(b'{"keys":[]}')
        temporary.replace(path)
        until(health, lambda value: value == 503)
        until(lambda: fixed("/probe")["status"], lambda value: value == 401)
    finally:
        temporary.write_bytes(public)
        temporary.replace(path)
    until(health, lambda value: value == 200)
    until(lambda: fixed("/probe")["status"], lambda value: value == 200)
    return {
        "readinessWithdrawn": True,
        "authenticationWithdrawn": True,
        "readinessRecovered": True,
        "authenticationRecovered": True,
    }


def queue():
    session = login()
    fixed("/reset", True)
    try:
        first = app(session, "/submit/localBlocker", True)["id"]
        until(lambda: fixed("/status"), lambda value: value["entered"])
        second = app(session, "/submit/localEffect", True)["id"]
        admitted = time.monotonic()
        assert app(session, "/executions/" + second)["status"] == "QUEUED"
        assert fixed("/status")["effects"] == 0
        while time.monotonic() - admitted < 2.5:
            assert app(session, "/executions/" + second)["status"] == "QUEUED"
            time.sleep(0.1)
        fixed("/release", True)
        assert terminal(session, first)["status"] == "COMPLETED"
        failed = terminal(session, second)
        assert (
            failed["status"] == "FAILED"
            and failed["failure"] == "execution credential expired before start"
        )
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline:
            assert fixed("/status")["effects"] == 0
            time.sleep(0.1)
    finally:
        fixed("/release", True)
    return {
        "queuedObserved": True,
        "expiredBeforeStart": True,
        "queuedEffects": 0,
        "freshPolling": True,
    }


def callbacks():
    alice = login()
    baseline = app(alice, "/callback-counts")
    execution = app(alice, "/submit/localOwned", True)["id"]
    success = terminal(alice, execution)
    assert success["status"] == "COMPLETED"
    assert json.loads(success["result"]) == {
        "issuer": "loomspan-app",
        "subject": "alice",
        "roles": ["ROLE_ORDER_EDITOR"],
        "credentialEqual": True,
    }
    assert app(alice, "/callback-counts") == {
        key: value + 1 for key, value in baseline.items()
    }
    denied = terminal(
        (literal := login("literal")),
        app(literal, "/submit/localLiteralOwned", True)["id"],
    )
    assert denied["status"] == "FAILED" and "403" in denied["failure"]
    assert app(alice, "/callback-counts") == {
        "arrivals": baseline["arrivals"] + 2,
        "bodies": baseline["bodies"] + 1,
        "effects": baseline["effects"] + 1,
    }
    denied = terminal((bob := login("bob")), app(bob, "/submit/localOwned", True)["id"])
    assert denied["status"] == "FAILED" and "403" in denied["failure"]
    assert app(alice, "/callback-counts") == {
        "arrivals": baseline["arrivals"] + 3,
        "bodies": baseline["bodies"] + 2,
        "effects": baseline["effects"] + 1,
    }
    # The same form chain still enforces CSRF after callback requests.
    assert request(alice[0], "http://127.0.0.1:8081/submit/localModel", {})[0] == 403
    assert (
        terminal(alice, app(alice, "/submit/localModel", True)["id"])["status"]
        == "COMPLETED"
    )
    return {
        "forwardedIdentity": True,
        "credentialEqual": True,
        "methodDenied": True,
        "ownershipDenied": True,
        "formAndCsrfPreserved": True,
    }


def callback_expiry():
    session = login()
    fixed("/reset", True)
    baseline = app(session, "/callback-counts")
    try:
        execution = app(session, "/submit/localCallbackPlanner", True)["id"]
        until(lambda: fixed("/status"), lambda value: value["entered"])
        assert app(session, "/executions/" + execution)["status"] == "RUNNING"
        entered = time.monotonic()
        # Fresh authenticated polling cannot renew the originally captured JWT.
        while time.monotonic() - entered < 2.5:
            assert app(session, "/executions/" + execution)["status"] == "RUNNING"
            assert app(session, "/callback-counts") == baseline
            time.sleep(0.1)
        fixed("/release", True)
        done = terminal(session, execution)
        assert (
            done["status"] == "FAILED"
            and done["failure"] == "HTTP caller credential missing or expired"
        )
        assert fixed("/status")["toolIssued"] is True
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline:
            assert app(session, "/callback-counts") == baseline
            time.sleep(0.1)
    finally:
        fixed("/release", True)
    return {
        "runningObserved": True,
        "plannerEntered": True,
        "exactChildFailure": True,
        "callbackArrivals": 0,
        "callbackBodies": 0,
        "callbackEffects": 0,
        "freshPolling": True,
    }


if __name__ == "__main__":
    try:
        result = {
            "issuance": issuance,
            "restart": restart,
            "trust": trust,
            "queue": queue,
            "callbacks": callbacks,
            "callback-expiry": callback_expiry,
        }[sys.argv[1]]()
        print(json.dumps(result))
    except Exception:
        # No raw response, exception or credential-bearing state crosses the boundary.
        print('{"failed":true}')
        raise SystemExit(1) from None
