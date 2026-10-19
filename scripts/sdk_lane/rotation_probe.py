"""Ordered real Standard two-app/JWKS oracles. No credentials leave fixture memory."""

import json
from pathlib import Path
import sys
import time

import local_probe as browser
import remote_probe

IDENTITY = {
    "issuer": "loomspan-app",
    "subject": "alice",
    "roles": ["ROLE_ORDER_EDITOR"],
    "credentialEqual": True,
}


def slot(name, receiver):
    return browser.fixed("/rotation/probe/" + name + "/" + receiver)


def boundary(name, sidecar, callback):
    assert slot(name, "sidecar")["status"] == sidecar
    result = slot(name, "callback")
    assert result["status"] == callback
    if callback == 200:
        assert result["identity"] == IDENTITY


def publish(receiver, source, name, expected):
    path = Path("/trust/" + receiver + ".json")
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(Path("/trust/" + source + ".json").read_bytes())
    temporary.replace(path)
    started = time.monotonic()
    while (
        slot(name, "sidecar" if receiver == "sidecar" else "callback")["status"]
        != expected
    ):
        assert time.monotonic() - started < 5
        time.sleep(0.1)
    assert time.monotonic() - started < 5


def public(name):
    return json.loads(Path("/public/" + name + ".json").read_text())["keys"][0]["kid"]


def add():
    # Use B's real browser authentication/SDK issuance, while callbacks target A.
    original = browser.request

    def from_b(opener, url, data=None, headers=None):
        return original(
            opener,
            url.replace("http://127.0.0.1:8081", "https://app:8445"),
            data,
            headers,
        )

    browser.request = from_b
    try:
        alice = browser.login()
        before = browser.app(alice, "/callback-counts")
        execution = browser.app(alice, "/submit/localOwned", True)["id"]
        done = browser.terminal(alice, execution)
        assert done["status"] == "COMPLETED" and json.loads(done["result"]) == IDENTITY
        # B has no callback effects: actual callback receiver is A.
        assert browser.app(alice, "/callback-counts") == before
        browser.app(browser.login("bob"), "/executions/" + execution, expected=404)
        browser.app(alice, "/capture", True)
        browser.fixed("/rotation/save-old")
        for user, skill in (("literal", "localLiteralOwned"), ("bob", "localOwned")):
            session = browser.login(user)
            result = browser.terminal(
                session, browser.app(session, "/submit/" + skill, True)["id"]
            )
            assert result["status"] == "FAILED" and "403" in result["failure"]
    finally:
        browser.request = original
    a = browser.login()
    assert browser.app(a, "/executions/" + execution)["status"] == "COMPLETED"
    assert browser.app(a, "/callback-counts") == {
        "arrivals": 3,
        "bodies": 2,
        "effects": 1,
    }
    assert public("app-a") == public("app-b") == slot("old", "metadata")["kid"]
    assert public("candidate") != public("app-a")
    assert slot("candidate", "metadata")["kid"] == public("candidate")
    boundary("old", 200, 200)
    boundary("candidate", 401, 401)
    publish("sidecar", "overlap", "candidate", 200)
    boundary("candidate", 200, 401)
    boundary("old", 200, 200)
    publish("callback", "overlap", "candidate", 200)
    boundary("candidate", 200, 200)
    boundary("old", 200, 200)
    # No normal signer has changed during addition.
    assert public("app-a") == public("app-b") == slot("old", "metadata")["kid"]


def retire():
    expected = public("candidate")
    assert public("app-a") == public("app-b") == expected
    alice = browser.login()
    browser.app(alice, "/rotation-capture", True)
    assert slot("current", "metadata")["kid"] == expected
    boundary("current", 200, 200)
    # Verify B's actual fresh SDK credential, not just the exported public file.
    status, body = browser.request(browser.fresh(), "https://app:8445/login")
    assert status == 200
    original = browser.request

    def from_b(opener, url, data=None, headers=None):
        return original(
            opener,
            url.replace("http://127.0.0.1:8081", "https://app:8445"),
            data,
            headers,
        )

    browser.request = from_b
    try:
        browser.app(browser.login(), "/rotation-capture", True)
    finally:
        browser.request = original
    assert slot("current", "metadata")["kid"] == expected
    boundary("current", 200, 200)
    boundary("old", 200, 200)
    assert slot("old", "metadata")["unexpired"] is True
    # Fixed marker files bridge the two protected namespaces without another listener.
    Path("/barrier/entered").unlink(missing_ok=True)
    Path("/barrier/release").unlink(missing_ok=True)
    work = slot("old", "blocker")
    assert work["status"] == 202
    browser.until(lambda: Path("/barrier/entered").exists(), bool, 10)
    assert browser.app(alice, "/executions/" + work["id"])["status"] == "RUNNING"
    try:
        publish("sidecar", "replacement", "old", 401)
        boundary("old", 401, 200)
        boundary("current", 200, 200)
        assert browser.app(alice, "/executions/" + work["id"])["status"] == "RUNNING"
        publish("callback", "replacement", "old", 401)
        before = browser.app(alice, "/callback-counts")
        boundary("old", 401, 401)
        after = browser.app(alice, "/callback-counts")
        assert (
            after["bodies"] == before["bodies"]
            and after["effects"] == before["effects"]
        )
        boundary("current", 200, 200)
        assert slot("old", "metadata")["unexpired"] is True
    finally:
        Path("/barrier/release").touch()
    assert browser.terminal(alice, work["id"]) == {
        "status": "COMPLETED",
        "result": "fixture result",
        "failure": "",
    }


def main(action):
    remote_probe.setup("standard", "trusted-group-rotation")
    if action == "add":
        add()
    elif action == "retire":
        retire()
    elif action == "release":
        Path("/barrier/release").touch()
    else:
        raise AssertionError("unknown action")
    return {"passed": True}


if __name__ == "__main__":
    try:
        print(json.dumps(main(sys.argv[1])))
    except Exception:
        print('{"failed":true}')
        raise SystemExit(1) from None
