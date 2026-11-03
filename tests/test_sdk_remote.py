"""Remote harness boundaries; real deployment evidence remains runner-owned."""

from datetime import datetime, timezone
from pathlib import Path
import socket
import ssl
import sys
import threading
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

import pytest
import yaml
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import ExtendedKeyUsageOID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sdk_lane import remote, remote_fault, remote_material
import run_sdk as runner


CHECKOUT = Path(__file__).resolve().parents[2] / "loomspan-sidecar"
ROOT = Path(__file__).resolve().parents[1]


def test_generated_material_rejects_wrong_ca_hostname_and_expiry_with_live_tls(
    tmp_path,
):
    remote_material.generate(tmp_path / "material")
    material = tmp_path / "material"
    for label, hostname, authority, expected in (
        ("app-server", "app", "group", None),
        ("app-wrong-ca-server", "app", "group", 20),
        ("app-wrong-host", "app", "group", 62),
        ("app-expired", "app", "group", 10),
    ):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(
            material / (label + ".pem"), material / (label + "-key.pem")
        )

        def serve():
            try:
                raw, _ = listener.accept()
                with raw:
                    try:
                        with server_context.wrap_socket(
                            raw, server_side=True
                        ) as stream:
                            stream.recv(1)
                    except OSError:
                        pass
            finally:
                listener.close()

        worker = threading.Thread(target=serve)
        worker.start()
        client_context = ssl.create_default_context(
            cafile=str(material / (authority + "-ca.pem"))
        )
        try:
            with socket.create_connection(listener.getsockname(), timeout=2) as raw:
                try:
                    with client_context.wrap_socket(
                        raw, server_hostname=hostname
                    ) as stream:
                        assert expected is None
                        stream.sendall(b"x")
                except ssl.SSLCertVerificationError as failure:
                    assert expected is not None and failure.verify_code == expected
        finally:
            worker.join(3)
            assert not worker.is_alive()
    # A missing listener is infrastructure failure, never certificate rejection.
    unavailable = socket.socket()
    unavailable.bind(("127.0.0.1", 0))
    address = unavailable.getsockname()
    unavailable.close()
    with pytest.raises((ConnectionRefusedError, TimeoutError)):
        socket.create_connection(address, timeout=2)


def test_remote_material_has_correct_purpose_and_is_unique(tmp_path):
    for directory in (tmp_path / "one", tmp_path / "two"):
        remote_material.generate(directory)
    directory = tmp_path / "one"

    def certificate(name):
        return x509.load_pem_x509_certificate(
            (directory / (name + ".pem")).read_bytes()
        )

    assert (directory / "group-ca.pem").read_bytes() != (
        tmp_path / "two/group-ca.pem"
    ).read_bytes()
    ca = certificate("group-ca")
    assert ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    for peer in ("app", "sidecar"):
        for kind, purpose in (
            ("server", ExtendedKeyUsageOID.SERVER_AUTH),
            ("client", ExtendedKeyUsageOID.CLIENT_AUTH),
        ):
            leaf = certificate(peer + "-" + kind)
            assert (
                purpose
                in leaf.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
            )
            assert leaf.issuer == ca.subject
        assert certificate(peer + "-wrong-ca-client").issuer != ca.subject
        assert certificate(peer + "-wrong-ca-server").issuer != ca.subject
        assert certificate(peer + "-expired").not_valid_after_utc < datetime.now(
            timezone.utc
        )
        assert "wrong.invalid" in certificate(
            peer + "-wrong-host"
        ).extensions.get_extension_for_class(
            x509.SubjectAlternativeName
        ).value.get_values_for_type(x509.DNSName)
    key = serialization.load_pem_private_key(
        (directory / "signing/signer-key.pem").read_bytes(), password=None
    )
    assert key.key_size == 2048
    assert b"BEGIN PRIVATE KEY" in (directory / "signing/signer-key.pem").read_bytes()


@pytest.mark.parametrize("recipe", ["standard", "hardened"])
def test_composition_exercises_shipped_fragments_and_separates_signer(tmp_path, recipe):
    remote_material.generate(tmp_path / "material")
    remote.configure(tmp_path / "config", CHECKOUT, recipe, "positive")
    document = remote.composition(tmp_path, ROOT, "image", "public-volume", recipe)
    services = document["services"]
    assert not any("ports" in service for service in services.values())
    assert not any("/signing" in mount for mount in services["sidecar"]["volumes"])
    assert "public:/public:ro" in services["sidecar"]["volumes"]
    assert any("/signing:ro" in mount for mount in services["app"]["volumes"])
    app = yaml.safe_load((tmp_path / "config/app.yaml").read_text())
    assert app["loomspan-sdk"]["signing"]["mode"] == "provided"
    config = yaml.safe_load((tmp_path / "config/sidecar/application.yaml").read_text())
    assert config["loomspan-sidecar"]["trust"] == {
        "mode": "file",
        "file": {"jwks": "/public/jwks.json"},
    }
    if recipe == "standard":
        assert not any("proxy" in name for name in services)
        assert app["loomspan-sdk"]["ssl-bundle"] == "sidecar"
        assert config["server"]["ssl"]["enabled"]
        assert not any("client-auth" in str(value) for value in (app, config))
        java_options = services["sidecar"]["environment"]["JAVA_TOOL_OPTIONS"]
        assert "-Djavax.net.ssl.trustStore=/tls/jvm-truststore.p12" in java_options
        assert "javax.net.ssl.keyStore=" not in java_options
        from cryptography.hazmat.primitives.serialization import pkcs12
        trust = pkcs12.load_pkcs12((tmp_path / "material/jvm-truststore.p12").read_bytes(), b"fixture-public-trust")
        assert trust.key is None
        assert [cert.certificate for cert in trust.additional_certs] == [
            x509.load_pem_x509_certificate((tmp_path / "material/group-ca.pem").read_bytes())
        ]
    else:
        for peer in ("app", "sidecar"):
            assert services[peer]["network_mode"] == "service:" + peer + "-proxy"
            assert (
                services[peer + "-fixture"]["network_mode"]
                == "service:" + peer + "-proxy"
            )
            text = (tmp_path / ("config/Caddyfile." + peer)).read_text()
            assert "bind 127.0.0.1" in text
            assert "require_and_verify" in text
            assert "tls_insecure_skip_verify" not in text
            assert "lb_try_duration 0" in text


@pytest.mark.parametrize("recipe", ["standard", "hardened"])
def test_remote_dispatch_runs_all_required_scenarios(tmp_path, monkeypatch, recipe):
    calls = []

    class Fake:
        def __init__(self, *args):
            self.variant = args[6]
            self.project, self.volume = (
                "unique-" + self.variant,
                "public-" + self.variant,
            )

        def start(self):
            calls.append(("start", self.variant))

        def run(self):
            calls.append(("run", self.variant))
            return (
                remote.observations(recipe, self.variant, "scenario")
                if self.variant != "isolation"
                else {"passed": True}
            )

        def cleanup(self):
            calls.append(("cleanup", self.variant))

    monkeypatch.setattr(remote, "Runtime", Fake)
    monkeypatch.setattr(runner, "command", lambda *args, **kwargs: "")
    report = {
        "recipe": recipe,
        "stages": {},
        "scenarioResults": {s: "not-run" for s in remote.scenarios(recipe)},
    }
    runner.run_remote(report, CHECKOUT, tmp_path)
    assert report["status"] == "passed"
    assert all(value == "passed" for value in report["scenarioResults"].values())
    assert calls == [
        (phase, v)
        for v in remote.VARIANTS[recipe]
        for phase in ("start", "run", "cleanup")
    ]


@pytest.mark.parametrize(
    "result", [{}, {"passed": False}, {"passed": 1}, {"passed": True, "extra": True}]
)
def test_remote_rejects_missing_false_extra_and_wrong_typed_results(tmp_path, result):
    runtime = remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "unique",
        "image",
        "standard",
        "positive",
        lambda *args, **kwargs: __import__("json").dumps(result),
        runner.LaneFailure,
    )
    with pytest.raises(runner.LaneFailure, match="invalid-result"):
        runtime.probe("scenario")


@pytest.mark.parametrize("mutation", ["missing", "false", "extra", "integer"])
def test_remote_observation_schema_is_strict(tmp_path, mutation):
    result = remote.observations("standard", "positive", "scenario")
    if mutation == "missing":
        del result["credentialEqual"]
    elif mutation == "false":
        result["credentialEqual"] = False
    elif mutation == "extra":
        result["extra"] = True
    else:
        result["credentialEqual"] = 1
    runtime = remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "unique",
        "image",
        "standard",
        "positive",
        lambda *args, **kwargs: json.dumps(result),
        runner.LaneFailure,
    )
    with pytest.raises(runner.LaneFailure, match="invalid-result"):
        runtime.probe("scenario")


def test_fixed_loss_instrument_forwards_once_after_receiver_effect(monkeypatch):
    class Receiver(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            assert self.path == "/loomspan/callbacks/owned"
            self.rfile.read(int(self.headers.get("Content-Length", "0")))
            self.server.effects += 1
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

    receiver = ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
    receiver.effects = 0
    fault = ThreadingHTTPServer(("127.0.0.1", 0), remote_fault.Handler)
    fault.state = remote_fault.State("hardened", "app")
    original = http.client.HTTPConnection

    def connection(host, port, **kwargs):
        return original(
            *(
                receiver.server_address
                if (host, port) == ("127.0.0.1", 8081)
                else (host, port)
            ),
            **kwargs,
        )

    monkeypatch.setattr(remote_fault.http.client, "HTTPConnection", connection)
    threads = [
        threading.Thread(target=server.serve_forever) for server in (receiver, fault)
    ]
    for thread in threads:
        thread.start()
    try:
        caller = original(*fault.server_address, timeout=3)
        caller.request("POST", "/loomspan/callbacks/owned", b"{}")
        with pytest.raises(http.client.RemoteDisconnected):
            caller.getresponse()
        caller.close()
        assert receiver.effects == 1
        assert fault.state.counts == {"attempts": 1, "forwards": 1, "accepted": 1}
        caller = original(*fault.server_address, timeout=3)
        caller.request(
            "POST", "http://unrelated.invalid/loomspan/callbacks/owned", b"{}"
        )
        assert caller.getresponse().status == 404
        caller.close()
        assert receiver.effects == 1
        assert fault.state.counts == {"attempts": 1, "forwards": 1, "accepted": 1}
    finally:
        for server in (receiver, fault):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(3)


@pytest.mark.parametrize("phase", ["start", "run", "cleanup"])
def test_remote_failure_cleans_and_cannot_pass(tmp_path, monkeypatch, phase):
    cleaned = []

    class Fake:
        def __init__(self, *args):
            self.project, self.volume = "unique", "unique-public"

        def start(self):
            if phase == "start":
                raise runner.LaneFailure("fixture-start")

        def run(self):
            if phase == "run":
                raise KeyboardInterrupt()
            return remote.observations("standard", "positive", "scenario")

        def cleanup(self):
            cleaned.append(True)
            if phase == "cleanup":
                raise runner.LaneFailure("fixture-cleanup")

    monkeypatch.setattr(remote, "Runtime", Fake)
    monkeypatch.setattr(runner, "command", lambda *args, **kwargs: "")
    report = {
        "recipe": "standard",
        "stages": {},
        "scenarioResults": {s: "not-run" for s in remote.scenarios("standard")},
    }
    with pytest.raises((runner.LaneFailure, KeyboardInterrupt)):
        runner.run_remote(report, CHECKOUT, tmp_path)
    assert cleaned == [True]
    assert "status" not in report
    assert report["scenarioResults"]["standard-positive"] == "failed"


@pytest.mark.parametrize("failure", [None, "down", "volume"])
def test_cleanup_is_project_scoped_and_attempts_public_volume_even_after_down_failure(
    failure,
):
    calls = []
    runtime = remote.Runtime.__new__(remote.Runtime)
    runtime.project = "sdk-unique-positive"
    runtime.volume = "sdk-unique-positive-public"
    runtime.compose = [
        "docker",
        "compose",
        "-p",
        runtime.project,
        "-f",
        "temporary-compose.yaml",
    ]

    def call(args, **kwargs):
        calls.append(args)
        if args[:3] == ["docker", "ps", "-aq"]:
            return "owned-helper"
        if ("down" in args and failure == "down") or (
            args[:3] == ["docker", "volume", "rm"] and failure == "volume"
        ):
            raise runner.LaneFailure("cleanup-failed")
        return ""

    runtime.call = call
    if failure:
        with pytest.raises(runner.LaneFailure):
            runtime.cleanup()
    else:
        runtime.cleanup()
    assert calls[0][-1] == "label=loomspan.sdk.helper=" + runtime.project
    assert calls[1] == ["docker", "rm", "--force", "owned-helper"]
    assert calls[-1] == ["docker", "volume", "rm", runtime.volume]
    assert "prune" not in str(calls)


@pytest.mark.parametrize("invalid", ["empty", "private", "wrong-key"])
def test_public_export_must_match_provided_signer_before_sidecar_start(
    tmp_path, invalid
):
    runtime = remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "unique",
        "image",
        "standard",
        "positive",
        lambda *args, **kwargs: "",
        runner.LaneFailure,
    )

    def encoded(number):
        import base64

        return (
            base64.urlsafe_b64encode(
                number.to_bytes((number.bit_length() + 7) // 8, "big")
            )
            .rstrip(b"=")
            .decode()
        )

    jwk = {
        "kty": "RSA",
        "n": encoded(runtime.signer_public.n),
        "e": encoded(runtime.signer_public.e),
    }
    public = {"keys": [jwk]}
    if invalid == "empty":
        public = {"keys": []}
    elif invalid == "private":
        jwk["d"] = "private-field-sentinel"
    else:
        jwk["n"] = encoded(runtime.signer_public.n + 2)
    calls = []

    def call(args, **kwargs):
        calls.append(args)
        return json.dumps(public) if "cat" in args else ""

    runtime.call = call
    runtime.wait = lambda *args: None
    with pytest.raises(runner.LaneFailure, match="public-export-invalid"):
        runtime.start()
    assert not any(args[-2:] == ["sidecar", "sidecar-fixture"] for args in calls)


def test_standard_group_rotation_has_two_apps_and_independent_trust_files(tmp_path):
    assert "trusted-group-rotation" in remote.VARIANTS["standard"]
    assert "trusted-group-rotation" not in remote.VARIANTS["hardened"]
    remote_material.generate(tmp_path / "material")
    remote.configure(
        tmp_path / "config", CHECKOUT, "standard", "trusted-group-rotation"
    )
    document = remote.composition(tmp_path, ROOT, "image", "public-volume", "standard")
    services = document["services"]
    assert services["app-b"]["network_mode"] == "service:app-network"
    assert (
        services["app"]["network_mode"]
        == services["app-fixture"]["network_mode"]
        == "service:app-network"
    )
    assert services["app-network"]["networks"] == {"remote": {"aliases": ["app"]}}
    mounts = services["app-fixture"]["volumes"]
    for module in ("rotation_probe", "remote_probe", "local_probe"):
        assert any(mount.endswith(":/" + module + ".py:ro") for mount in mounts)
    for name in ("app-fixture", "sidecar-fixture"):
        assert any(mount.endswith(":/barrier") for mount in services[name]["volumes"])
    assert not any("ports" in service for service in services.values())
    a = yaml.safe_load((tmp_path / "config/app.yaml").read_text())
    b = yaml.safe_load((tmp_path / "config/app-b.yaml").read_text())
    assert b["server"]["port"] == 8445
    assert a["loomspan-sdk"]["issuance"] == b["loomspan-sdk"]["issuance"]
    assert (
        a["loomspan-sdk"]["signing"]["provided"]["key-location"]
        == b["loomspan-sdk"]["signing"]["provided"]["key-location"]
    )
    assert (
        a["loomspan-sdk"]["signing"]["provided"]["jwks-export"]
        != b["loomspan-sdk"]["signing"]["provided"]["jwks-export"]
    )
    assert a["loomspan-sdk"]["callbacks"]["overlap-jwks"] == "/trust/callback.json"
    sidecar = yaml.safe_load((tmp_path / "config/sidecar/application.yaml").read_text())
    assert sidecar["loomspan-sidecar"]["trust"]["file"]["jwks"] == "/trust/sidecar.json"
    assert any(":/trust:ro" in mount for mount in services["sidecar"]["volumes"])
    assert not any("/signing" in mount for mount in services["sidecar"]["volumes"])


@pytest.mark.parametrize("recipe", ["standard", "hardened"])
def test_outbound_only_omits_callbacks_and_preserves_recipe_invocation(
    tmp_path, recipe
):
    remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "unique",
        "image",
        recipe,
        "outbound-only",
        lambda *a, **k: "",
        runner.LaneFailure,
    )
    directory = tmp_path / "runtime"
    document = yaml.safe_load((directory / "compose.yaml").read_text())
    app = yaml.safe_load((directory / "config/app.yaml").read_text())
    config = yaml.safe_load((directory / "config/sidecar/application.yaml").read_text())
    assert not (directory / "config/sidecar/routes.yaml").exists()
    assert config["loomspan"]["executor-config"] == {"default": {"http": {}}}
    assert config["loomspan"]["skills"]["locations"] == ["file:/config/localModel.yaml"]
    assert set(p.name for p in (directory / "config/sidecar").glob("local*.yaml")) == {
        "localModel.yaml"
    }
    assert (
        "--spring.main.web-application-type=none"
        in document["services"]["app"]["command"]
    )
    assert app["loomspan-sdk"]["signing"]["mode"] == "provided"
    if recipe == "standard":
        assert app["loomspan-sdk"]["base-url"] == "https://sidecar:8443"
        assert app["loomspan-sdk"]["ssl-bundle"] == "sidecar"
    else:
        a = (directory / "config/Caddyfile.app").read_text()
        s = (directory / "config/Caddyfile.sidecar").read_text()
        assert (
            "https://:8443" not in a and ":8444" not in a and "127.0.0.1:8081" not in a
        )
        assert "http://:9080" in a and "tls_client_auth /tls/app-client.pem" in a
        assert "http://:9080" not in s and "app-proxy" not in s
        assert "https://:8443" in s and "require_and_verify" in s
        assert "tls_insecure_skip_verify" not in a + s


@pytest.mark.parametrize("variant", ["trusted-group-rotation", "outbound-only"])
@pytest.mark.parametrize("mutation", ["missing", "false", "integer", "extra"])
def test_new_scenarios_require_every_exact_typed_observation(
    tmp_path, variant, mutation
):
    expected = remote.observations("standard", variant, "scenario")
    runtime = remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "unique",
        "image",
        "standard",
        variant,
        lambda *a, **k: "",
        runner.LaneFailure,
    )
    for field in expected:
        value = dict(expected)
        if mutation == "missing":
            del value[field]
        elif mutation == "extra":
            value["extra"] = True
        elif mutation == "integer":
            value[field] = 1 if isinstance(value[field], bool) else True
        else:
            value[field] = False
        runtime.call = lambda *a, **k: json.dumps(value)
        with pytest.raises(runner.LaneFailure, match="invalid-result"):
            runtime.probe("scenario")


@pytest.mark.parametrize("failure", [None, "add", "restart", "retire"])
def test_group_rotation_orders_probes_both_restarts_and_always_releases(
    tmp_path, failure
):
    runtime = remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "unique",
        "image",
        "standard",
        "trusted-group-rotation",
        lambda *a, **k: "",
        runner.LaneFailure,
    )
    calls = []

    def call(args, **kwargs):
        if "/rotation_probe.py" in args:
            calls.append(args[-1])
            if args[-1] == failure:
                raise runner.LaneFailure("fixture-probe-failed")
            return '{"passed":true}'
        if "restart" in args:
            calls.append("restart-" + args[-1])
            config = yaml.safe_load(
                (runtime.directory / "config" / (args[-1] + ".yaml")).read_text()
            )
            assert (
                config["loomspan-sdk"]["signing"]["provided"]["key-location"]
                == "/replacement/signer-key.pem"
            )
            if failure == "restart":
                raise runner.LaneFailure("fixture-restart-failed")
        else:
            calls.append("candidate")
        return ""

    runtime.call = call
    runtime.wait = lambda name: calls.append(name)
    if failure:
        with pytest.raises(runner.LaneFailure):
            runtime.rotation()
    else:
        assert runtime.rotation() == remote.observations(
            "standard", "trusted-group-rotation", "scenario"
        )
        assert calls == [
            "candidate",
            "add",
            "restart-app",
            "app-ready",
            "restart-app-b",
            "app-b-ready",
            "retire",
            "release",
        ]
    assert calls[-1] == "release"
    if failure in ("add", "restart"):
        assert "retire" not in calls


def test_rotation_publication_has_five_second_bound_and_separate_files(
    tmp_path, monkeypatch
):
    sys.path.insert(0, str(ROOT / "scripts/sdk_lane"))
    import rotation_probe

    (tmp_path / "sidecar.json").write_text('{"keys":["old"]}')
    (tmp_path / "callback.json").write_text('{"keys":["old"]}')
    (tmp_path / "overlap.json").write_text('{"keys":["old","new"]}')
    monkeypatch.setattr(rotation_probe, "Path", lambda path: tmp_path / Path(path).name)
    monkeypatch.setattr(rotation_probe, "slot", lambda *a: {"status": 401})
    times = iter((0, 1, 6))
    monkeypatch.setattr(rotation_probe.time, "monotonic", lambda: next(times))
    monkeypatch.setattr(rotation_probe.time, "sleep", lambda *a: None)
    with pytest.raises(AssertionError):
        rotation_probe.publish("sidecar", "overlap", "candidate", 200)
    assert json.loads((tmp_path / "sidecar.json").read_text()) == {
        "keys": ["old", "new"]
    }
    assert json.loads((tmp_path / "callback.json").read_text()) == {"keys": ["old"]}


@pytest.mark.parametrize("variant", ["trusted-group-rotation", "outbound-only"])
@pytest.mark.parametrize("phase", ["start", "run", "cleanup"])
def test_new_scenario_failure_always_cleans_owned_resources(
    tmp_path, monkeypatch, variant, phase
):
    cleaned = []

    class Broken:
        project, volume = "sdk-owned-new", "sdk-owned-new-public"

        def __init__(self, *args):
            pass

        def start(self):
            if phase == "start":
                raise runner.LaneFailure("fixture-second-app-or-outbound-start-failed")

        def run(self):
            if phase == "run":
                raise runner.LaneFailure("fixture-publication-or-invocation-failed")
            return remote.observations("standard", variant, "scenario")

        def cleanup(self):
            cleaned.append(self.project)
            if phase == "cleanup":
                raise runner.LaneFailure("fixture-cleanup-failed")

    monkeypatch.setitem(remote.VARIANTS, "standard", (variant,))
    monkeypatch.setattr(remote, "Runtime", Broken)
    monkeypatch.setattr(runner, "command", lambda *a, **k: "")
    report = {
        "recipe": "standard",
        "stages": {},
        "scenarioResults": {"standard-" + variant: "not-run"},
    }
    with pytest.raises(runner.LaneFailure):
        runner.run_remote(report, CHECKOUT, tmp_path)
    assert cleaned == ["sdk-owned-new"]
    assert report["scenarioResults"]["standard-" + variant] == "failed"
    assert report.get("status") != "passed"


def test_group_second_app_start_failure_is_not_silently_skipped(tmp_path):
    calls = []
    runtime = remote.Runtime(
        tmp_path / "runtime",
        CHECKOUT,
        ROOT,
        "owned",
        "image",
        "standard",
        "trusted-group-rotation",
        lambda *a, **k: "",
        runner.LaneFailure,
    )

    def call(args, **kwargs):
        calls.append(args)
        if args[-3:] == ["up", "-d", "app-b"]:
            raise runner.LaneFailure("fixture-second-app-failed")
        return ""

    runtime.call = call
    runtime.wait = lambda *a: None
    with pytest.raises(runner.LaneFailure, match="second-app"):
        runtime.start()
    runtime.cleanup()
    assert calls[-1] == ["docker", "volume", "rm", runtime.volume]
    assert any("down" in args for args in calls)
