"""Fixed remote oracles; credentials and responses never leave this process."""

import http.client
import json
from pathlib import Path
import socket
import ssl
import sys
import time
import urllib.request

import local_probe as browser
from remote_contract import observations


def context(peer=None, authority="group"):
    value = ssl.create_default_context(cafile="/tls/" + authority + "-ca.pem")
    if peer:
        value.load_cert_chain(
            "/tls/" + peer + "-client.pem", "/tls/" + peer + "-client-key.pem"
        )
    return value


def https(
    host,
    port,
    path,
    peer=None,
    method="GET",
    body=None,
    expected=None,
    host_header=None,
):
    connection = http.client.HTTPSConnection(
        host, port, context=context(peer), timeout=3
    )
    try:
        connection.request(method, path, body, {"Host": host_header or host})
        response = connection.getresponse()
        data = response.read(1024 * 1024)
        if expected is not None:
            assert response.status == expected
        return response.status, data
    finally:
        connection.close()


def verification_error(host, port, peer=None, client_kind="client"):
    value = context()
    if peer:
        value.load_cert_chain(
            "/tls/" + peer + "-" + client_kind + ".pem",
            "/tls/" + peer + "-" + client_kind + "-key.pem",
        )
    try:
        with socket.create_connection((host, port), timeout=3) as raw:
            with value.wrap_socket(raw, server_hostname=host) as stream:
                stream.sendall(
                    b"GET /v1/skills HTTP/1.1\r\nHost: fixture\r\nConnection: close\r\n\r\n"
                )
                stream.recv(4096)
    except ssl.SSLCertVerificationError as failure:
        return failure.verify_code
    except ssl.SSLError:
        return "peer-alert"
    raise AssertionError("TLS unexpectedly accepted")


def setup(recipe, variant):
    base = "https://app:8443" if recipe == "standard" else "https://app-proxy:8444"
    original_request = browser.request
    original_fresh = browser.fresh
    browser_context = context()
    if recipe == "standard" and variant in ("callback-host", "callback-expired"):
        # Negative receiver material also covers Spring's browser listener. Only
        # this test driver pins the exact supplied certificate to control the app.
        # The real Sidecar caller always uses normal chain/hostname verification.
        browser_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        browser_context.check_hostname = False
        browser_context.verify_mode = ssl.CERT_NONE
        label = "wrong-host" if variant == "callback-host" else "expired"
        expected = ssl.PEM_cert_to_DER_cert(
            Path("/tls/app-" + label + ".pem").read_text()
        )
        with socket.create_connection(("app", 8443), timeout=3) as raw:
            with browser_context.wrap_socket(raw, server_hostname="app") as stream:
                assert stream.getpeercert(binary_form=True) == expected

    def fresh():
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPCookieProcessor(
                __import__("http.cookiejar", fromlist=["CookieJar"]).CookieJar()
            ),
            urllib.request.HTTPSHandler(context=browser_context),
        )

    def request(opener, url, data=None, headers=None):
        return original_request(
            opener, url.replace("http://127.0.0.1:8081", base), data, headers
        )

    browser.fresh = fresh
    browser.request = request
    return original_fresh


def ready(recipe, variant, peer):
    if peer in ("app", "app-b"):
        # Login readiness is distinct from all credential/negative oracles.
        status, _ = browser.request(
            browser.fresh(),
            "https://app:8445/login"
            if peer == "app-b"
            else "http://127.0.0.1:8081/login",
        )
        assert status == 200
        return
    host = "sidecar" if recipe == "standard" else "sidecar-proxy"
    if variant == "invocation-server":
        assert verification_error(
            host, 8443, "app" if recipe == "hardened" else None
        ) in (20, 21, 19)
        # Verify the live supplied wrong-CA endpoint with its own CA, independently.
        conn = http.client.HTTPSConnection(
            host,
            8443,
            context=context("app" if recipe == "hardened" else None, "other"),
            timeout=3,
        )
        try:
            conn.request("GET", "/actuator/health/readiness")
            response = conn.getresponse()
            assert response.status == 200 and json.loads(response.read()) == {
                "status": "UP"
            }
        finally:
            conn.close()
    else:
        _, body = https(
            host,
            8443,
            "/actuator/health/readiness",
            "app" if recipe == "hardened" else None,
            expected=200,
        )
        assert json.loads(body) == {"status": "UP"}


def scenario(recipe, variant):
    session = browser.login()
    if variant == "positive":
        assert browser.callbacks() == {
            "forwardedIdentity": True,
            "credentialEqual": True,
            "methodDenied": True,
            "ownershipDenied": True,
            "formAndCsrfPreserved": True,
        }
        https(
            "sidecar" if recipe == "standard" else "sidecar-proxy",
            8443,
            "/v1/skills",
            "app" if recipe == "hardened" else None,
            expected=401,
        )
        return
    before = browser.app(session, "/callback-counts")
    if variant.startswith("invocation-"):
        status, _ = browser.request(
            session[0], "http://127.0.0.1:8081/submit/localOwned", {}, session[1]
        )
        assert status == (500 if recipe == "standard" else 502)
        assert browser.app(session, "/callback-counts") == before
        host = "sidecar" if recipe == "standard" else "sidecar-proxy"
        if variant == "invocation-server":
            assert verification_error(
                host, 8443, "app" if recipe == "hardened" else None
            ) in (19, 20, 21)
        else:
            assert (
                verification_error(host, 8443, "app", "wrong-ca-client") == "peer-alert"
            )
            https(host, 8443, "/v1/skills", "app", expected=401)
        return
    if variant.startswith("callback-") and variant != "callback-loss":
        execution = browser.app(session, "/submit/localOwned", True)["id"]
        assert browser.terminal(session, execution)["status"] == "FAILED"
        assert browser.app(session, "/callback-counts") == before
        host = "app" if recipe == "standard" else "app-proxy"
        if variant == "callback-client":
            assert (
                verification_error(host, 8443, "sidecar", "wrong-ca-client")
                == "peer-alert"
            )
            https(
                host,
                8443,
                "/loomspan/callbacks/owned",
                "sidecar",
                method="POST",
                body=b"{}",
                expected=401,
            )
        else:
            code = verification_error(
                host, 8443, "sidecar" if recipe == "hardened" else None
            )
            assert code in (
                {62}
                if variant == "callback-host"
                else {10}
                if variant == "callback-expired"
                else {19, 20, 21}
            )
        return
    if variant == "submission-loss":
        status, body = browser.request(
            session[0], "http://127.0.0.1:8081/loss-submit", {}, session[1]
        )
        assert status == 200
        assert json.loads(body) == {
            "acceptanceUnknown": recipe == "standard",
            "httpFailure": recipe == "hardened",
        }
    elif variant == "callback-loss":
        execution = browser.app(session, "/submit/localOwned", True)["id"]
        assert browser.terminal(session, execution)["status"] == "FAILED"
        assert browser.app(session, "/callback-counts") == {
            key: value + 1 for key, value in before.items()
        }
    else:
        raise AssertionError("unknown variant")
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if variant == "callback-loss":
            assert browser.app(session, "/callback-counts") == {
                key: value + 1 for key, value in before.items()
            }
        time.sleep(0.2)


def isolation():
    for peer, backend in (("app", 8081), ("sidecar", 8080)):
        host = peer + "-proxy"
        for port in (backend, 9080, 8090, 9081):
            try:
                with socket.create_connection((host, port), timeout=2):
                    raise AssertionError("bypass listener reachable")
            except ConnectionRefusedError:
                pass
        assert verification_error(host, 8443) == "peer-alert"
    https("app-proxy", 8444, "/login", expected=200)
    https(
        "app-proxy",
        8444,
        "/loomspan/callbacks/owned",
        method="POST",
        body=b"{}",
        expected=404,
    )
    https("app-proxy", 8443, "/login", "sidecar", expected=404)
    https("sidecar-proxy", 8443, "/v1/skills", "app", expected=401)


def fixed(peer):
    # Absolute-form URI/authority cannot redirect either loopback gateway.
    target = "/v1/skills" if peer == "app" else "/loomspan/callbacks/owned"
    for path in (target, "http://127.0.0.1:8090/effect"):
        conn = http.client.HTTPConnection("127.0.0.1", 9080, timeout=3)
        try:
            conn.request(
                "POST" if peer == "sidecar" or path.startswith("http:") else "GET",
                path,
                headers={"Host": "127.0.0.1:8090"},
            )
            response = conn.getresponse()
            assert response.status in (401, 404, 405)
            response.read()
        finally:
            conn.close()
    assert browser.fixed("/status")["effects"] == 0


def main(recipe, variant, action):
    setup(recipe, variant)
    if action.endswith("-ready"):
        if action == "fault-ready":
            conn = http.client.HTTPConnection("127.0.0.1", 9082, timeout=3)
            conn.request("GET", "/counts")
            assert conn.getresponse().status == 200
            conn.close()
        else:
            ready(recipe, variant, action.removesuffix("-ready"))
    elif action == "scenario":
        scenario(recipe, variant)
    elif action == "isolation":
        isolation()
    elif action.startswith("fixed-"):
        fixed(action.split("-")[1])
    elif action == "loss-counts":
        conn = http.client.HTTPConnection("127.0.0.1", 9082, timeout=3)
        conn.request("GET", "/counts")
        response = conn.getresponse()
        assert response.status == 200
        assert json.loads(response.read()) == {
            "attempts": 1,
            "forwards": 1,
            "accepted": 1,
        }
        conn.close()
        if variant == "submission-loss":
            assert browser.fixed("/status")["effects"] == 1
    else:
        raise AssertionError("unknown action")
    return observations(recipe, variant, action)


if __name__ == "__main__":
    try:
        print(json.dumps(main(*sys.argv[1:])))
    except Exception:
        print('{"failed":true}')
        raise SystemExit(1) from None
