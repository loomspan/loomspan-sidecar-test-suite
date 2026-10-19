"""Provider-free SDK lane orchestration and failure evidence."""

import hashlib
import base64
import json
import subprocess
import sys
from pathlib import Path
import threading
from types import SimpleNamespace
import zipfile

import httpx
import pytest
import yaml
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


import run_sdk as runner
from sdk_lane.fixture import FixtureServer, LocalServer, LossProxy


SENTINELS = ("secret-provider-123", "PRIVATE-KEY-456", "business-payload-789")


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / "actual-sidecar"
    root.mkdir()
    (root / "pom.xml").write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><properties>'
        "<loomspan.version>1.0.0-beta.8</loomspan.version></properties></project>"
    )
    (root / "Dockerfile").touch()
    (root / "sdks/java").mkdir(parents=True)
    (root / "sdks/java/pom.xml").touch()
    sample = root / "examples/quickstart/compose.yaml"
    sample.parent.mkdir(parents=True)
    sample.write_bytes(
        (
            runner.ROOT.parent / "loomspan-sidecar/examples/quickstart/compose.yaml"
        ).read_bytes()
    )
    target = root / "target"
    target.mkdir()
    with zipfile.ZipFile(target / "sidecar.jar", "w") as archive:
        archive.writestr(
            "BOOT-INF/lib/loomspan-spring-boot-starter-1.0.0-beta.8.jar", b"fixture"
        )
    for module, artifact in (
        ("core", "loomspan-sdk-core"),
        ("spring-boot-starter", "loomspan-sdk-spring-boot-starter"),
    ):
        target = root / "sdks/java" / module / "target"
        target.mkdir(parents=True)
        with zipfile.ZipFile(target / f"{artifact}.jar", "w") as archive:
            archive.writestr(
                f"META-INF/maven/ai.loomspan/{artifact}/pom.properties",
                f"groupId=ai.loomspan\nartifactId={artifact}\nversion=0.1.0-SNAPSHOT\n",
            )
    return root


@pytest.fixture
def fake_lane(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(runner.shutil, "which", lambda tool: tool)

    def command(args, **kwargs):
        calls.append((list(map(str, args)), kwargs))
        if args[:3] == ["git", "rev-parse", "HEAD"]:
            return "a" * 40
        if args[:2] == ["git", "status"]:
            return "?? sdks/"
        return ""

    monkeypatch.setattr(runner, "command", command)
    original_find = runner.find_jar
    driver = tmp_path / "driver.jar"
    driver.write_bytes(b"plain-java-driver")
    boot = tmp_path / "boot.jar"
    boot.write_bytes(b"boot-reference")
    monkeypatch.setattr(
        runner,
        "find_jar",
        lambda directory: driver
        if directory == runner.ROOT / "sdk/driver/target"
        else boot
        if directory == runner.ROOT / "sdk/reference-app/target"
        else original_find(directory),
    )

    class Runtime:
        def __init__(self, directory, checkout, project):
            assert project.startswith("sdk-")
            self.project = project
            self.image = "fixture-image"

        def image_build(self):
            calls.append("imageBuild")

        def start(self):
            calls.append("startup")

        def readiness(self):
            calls.append("readiness")
            return {"status": "UP"}

        def shutdown(self):
            calls.append("shutdown")
            return {"exitCode": 143, "graceful": True, "oomKilled": False}

        def fixture(self):
            calls.append("fixture")
            return {
                "modelRequests": 1,
                "syntheticEffects": 1,
                "submissionAttempts": 1,
                "forwardAttempts": 1,
            }

        def startup_fixture(self):
            calls.append("startupFixture")
            return {"modelRequests": 0}

        def blocking_client(self):
            calls.append("blockingClient")
            return {
                "completed": True,
                "opaqueResultPreserved": True,
                "failed": True,
                "primaryFailurePreserved": True,
                "acceptanceUnknown": True,
            }

        def shutdown_scenario(self, cutoff):
            calls.append("shutdownCutoff" if cutoff else "shutdownCompletion")
            return {"finished": not cutoff}

        def deployment_transport(self):
            calls.append("deploymentTransport")
            return {"trusted": True}

        def cleanup(self):
            calls.append("cleanup")

    monkeypatch.setattr(runner, "Runtime", Runtime)

    class LocalRuntime:
        def __init__(self, directory, checkout, root, project, image, call, failure):
            self.project = project + "-local"
            self.volume = self.project + "-keys"
            self.sample_hash = "b" * 64

        def start(self):
            calls.append("localStartup")

        def probe(self, name):
            calls.append("local-" + name)
            return runner.local.RESULTS[name]

        def restart(self):
            return self.probe("restart") | {"kidChanged": True}

        def cleanup(self):
            calls.append("localCleanup")

    monkeypatch.setattr(runner.local, "Runtime", LocalRuntime)
    return calls


def invoke(checkout, tmp_path, recipe="local"):
    output = tmp_path / "report"
    code = runner.main(
        [recipe, "--sidecar-checkout", str(checkout), "--output", str(output)]
    )
    return code, json.loads((output / "report.json").read_bytes())


def test_local_recipe_builds_boot_consumer_and_records_colocated_scenarios(
    checkout, tmp_path, fake_lane
):
    code, report = invoke(checkout, tmp_path)
    assert code == 0
    commands = [item[0] for item in fake_lane if isinstance(item, tuple)]
    assert any(
        str(runner.ROOT / "sdk/reference-app/pom.xml") in args for args in commands
    )
    assert report["referenceApp"]["sha256"]
    assert report["suiteSource"]["revision"]
    assert report["localRecipe"]["sampleSha256"]
    for name in (
        "local-issuance-roles",
        "local-ownership",
        "local-restart",
        "local-trust-recovery",
        "local-queue-expiry",
        "local-callback-authorization",
        "local-callback-expiry",
    ):
        assert report["scenarioResults"][name] == "passed"


def test_local_composition_preserves_shipped_colocated_boundary(checkout, tmp_path):
    document, source_hash = runner.local.composition(
        checkout, runner.ROOT, tmp_path, "unique-image", "unique-keys"
    )
    sidecar = document["services"]["sidecar"]
    host = document["services"]["host"]
    assert sidecar["user"] == host["user"] == "10001:10001"
    assert sidecar["environment"]["SERVER_ADDRESS"] == "127.0.0.1"
    assert sidecar["environment"]["LOOMSPAN_SIDECAR_TRUST_MODE"] == "colocated"
    assert (
        sidecar["environment"]["LOOMSPAN_SIDECAR_TRUST_COLOCATED_KEY_DIRECTORY"]
        == "/sidecar/keys"
    )
    assert "sidecar-keys:/sidecar/keys:ro" in sidecar["volumes"]
    assert "sidecar-keys:/keys" in host["volumes"]
    assert host["network_mode"] == "service:sidecar"
    assert host["depends_on"]["sidecar"]["condition"] == "service_started"
    assert document["networks"]["sdk"]["internal"]
    assert document["volumes"] == {
        "sidecar-keys": {"external": True, "name": "unique-keys"}
    }
    assert all("ports" not in service for service in document["services"].values())
    serialized = json.dumps(document)
    assert all(
        value not in serialized
        for value in ("docker.sock", ".runtime", "SMTP", "PASSWORD", "ingress")
    )
    sample = checkout / "examples/quickstart/compose.yaml"
    changed = yaml.safe_load(sample.read_bytes())
    changed["services"]["sidecar"]["healthcheck"]["interval"] = "7s"
    sample.write_text(yaml.safe_dump(changed))
    actual, changed_hash = runner.local.composition(
        checkout, runner.ROOT, tmp_path, "unique-image", "unique-keys"
    )
    assert actual["services"]["sidecar"]["healthcheck"]["interval"] == "7s"
    assert source_hash != changed_hash
    sample.unlink()
    with pytest.raises(FileNotFoundError):
        runner.local.composition(
            checkout, runner.ROOT, tmp_path, "unique-image", "unique-keys"
        )


def test_local_capture_and_probe_keep_credentials_in_memory(capsys):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    seen = []

    class Destination(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            seen.append((self.path, self.headers.get("Authorization")))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"[]")

    backend = ThreadingHTTPServer(("127.0.0.1", 0), Destination)
    fixture = LocalServer(("127.0.0.1", 0), ("127.0.0.1", backend.server_port))
    threads = [
        threading.Thread(target=server.serve_forever, daemon=True)
        for server in (backend, fixture)
    ]
    for thread in threads:
        thread.start()
    token = "Bearer " + SENTINELS[0]
    responses = []
    try:
        with httpx.Client(trust_env=False, timeout=3) as client:
            base = f"http://127.0.0.1:{fixture.server_port}"
            assert client.get(base + "/probe").status_code == 409
            assert client.get(base + "/capture/v1/skills").status_code == 400
            response = client.get(
                base + "/capture/v1/skills", headers={"Authorization": token}
            )
            assert response.status_code == 200 and response.json() == []
            responses.append(response.text)
            response = client.get(base + "/probe")
            assert response.json() == {"status": 200}
            responses.append(response.text)
            assert seen == [("/v1/skills", token)]
            for candidate, equal in (
                (token, True),
                ("Bearer wrong", False),
                ("", False),
            ):
                response = client.get(
                    base + "/compare", headers={"Authorization": candidate}
                )
                assert response.json() == {"equal": equal}
                responses.append(response.text)

            for route in (
                "/headers",
                "/probe?url=http://example.invalid",
                "/capture/arbitrary",
            ):
                assert (
                    client.get(
                        base + route, headers={"Authorization": token}
                    ).status_code
                    == 404
                )
            # Send the oversized declared length without transmitting its body:
            # rejection happens at headers, avoiding platform TCP reset races.
            from http.client import HTTPConnection

            oversized = HTTPConnection("127.0.0.1", fixture.server_port, timeout=3)
            oversized.putrequest("POST", "/effect")
            oversized.putheader("Content-Length", str(1024 * 1024 + 1))
            oversized.endheaders()
            assert oversized.getresponse().status == 413
            oversized.close()
            assert client.get(base + "/status").json()["effects"] == 0
            client.post(base + "/reset", json={})
            assert fixture.credential is None
            assert client.get(base + "/probe").status_code == 409
        assert all(
            value not in str(responses) + str(capsys.readouterr())
            for value in SENTINELS
        )
    finally:
        for server in (backend, fixture):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)
    assert fixture.credential is None


def test_local_queue_fixture_has_bounded_barrier_and_independent_effect_count(capsys):
    fixture = LocalServer(("127.0.0.1", 0))
    server = threading.Thread(target=fixture.serve_forever, daemon=True)
    server.start()
    completed = threading.Event()
    errors = []

    def blocker():
        try:
            with httpx.Client(trust_env=False, timeout=4) as client:
                assert (
                    client.post(
                        base + "/block/chat/completions", content=SENTINELS[2]
                    ).status_code
                    == 200
                )
                completed.set()
        except BaseException as error:
            errors.append(type(error).__name__)

    base = f"http://127.0.0.1:{fixture.server_port}"
    worker = threading.Thread(target=blocker)
    try:
        worker.start()
        assert fixture.entered.wait(2)
        assert not completed.is_set()
        with httpx.Client(trust_env=False, timeout=3) as client:
            assert client.get(base + "/status").json() == {
                "entered": True,
                "models": 1,
                "effects": 0,
                "toolIssued": False,
            }
            client.post(base + "/release", json={})
            assert completed.wait(2)
            client.post(base + "/effect", json={})
            assert client.get(base + "/status").json()["effects"] == 1
            assert client.post(base + "/unknown", json={}).status_code == 404
            client.post(base + "/reset", json={})
            assert client.get(base + "/status").json() == {
                "entered": False,
                "models": 0,
                "effects": 0,
                "toolIssued": False,
            }
        assert not errors
        assert all(value not in str(capsys.readouterr()) for value in SENTINELS)
    finally:
        fixture.release.set()
        worker.join(timeout=2)
        fixture.shutdown()
        fixture.server_close()
        server.join(timeout=2)


@pytest.mark.parametrize(
    "phase",
    [
        "start",
        "issuance",
        "restart",
        "trust",
        "queue",
        "callbacks",
        "callback-expiry",
        "cleanup",
        "interrupt",
    ],
)
def test_local_failures_and_interruptions_clean_unique_resources_without_secrets(
    checkout, tmp_path, fake_lane, monkeypatch, capsys, phase
):
    original = runner.local.Runtime.probe

    def fail(*args):
        if phase == "interrupt":
            raise KeyboardInterrupt(SENTINELS[0])
        raise runner.LaneFailure("local-fixture-failed")

    if phase in ("start", "cleanup", "restart"):
        monkeypatch.setattr(runner.local.Runtime, phase, fail)
    else:

        def probe(self, name):
            if name == phase or phase == "interrupt":
                fail()
            return original(self, name)

        monkeypatch.setattr(runner.local.Runtime, "probe", probe)
    code, report = invoke(checkout, tmp_path)
    assert code == 1
    assert report["diagnostic"] in (
        "local-fixture-failed",
        "local-cleanup-failed",
        "interrupted",
    )
    assert report["stages"]["localCleanup"]["status"] in ("passed", "failed")
    assert fake_lane[-1] == "cleanup"
    assert all(
        value not in json.dumps(report) + str(capsys.readouterr())
        for value in SENTINELS
    )
    assert (
        not all(result == "passed" for result in report["scenarioResults"].values())
        or phase == "cleanup"
    )


def test_local_runtime_prepares_and_removes_only_unique_external_volume(
    checkout, tmp_path
):
    calls = []
    instance = runner.local.Runtime(
        tmp_path / "local",
        checkout,
        runner.ROOT,
        "sdk-unique",
        "image",
        lambda args, **kwargs: calls.append(args),
        runner.LaneFailure,
    )

    # Inspect initialization before deliberately stopping startup at Compose.
    def call(args, **kwargs):
        calls.append(args)
        if "up" in args:
            raise runner.LaneFailure("startup-failed")

    instance.call = call
    with pytest.raises(runner.LaneFailure):
        instance.start()
    instance.cleanup()
    assert calls[0] == [
        "docker",
        "volume",
        "create",
        "--label",
        "com.docker.compose.project=sdk-unique-local",
        "sdk-unique-local-keys",
    ]
    assert calls[-1] == ["docker", "volume", "rm", "sdk-unique-local-keys"]
    assert "chown 10001:10001 /keys && chmod 0700 /keys" in calls[1]


@pytest.mark.parametrize(
    "result",
    [
        {},
        {"formLogin": True},
        {**runner.local.RESULTS["issuance"], "csrf": False},
        {**runner.local.RESULTS["issuance"], "csrf": 1},
    ],
)
def test_local_partial_or_false_results_fail(checkout, tmp_path, result):
    instance = runner.local.Runtime(
        tmp_path / "local",
        checkout,
        runner.ROOT,
        "sdk-unique",
        "image",
        lambda *args, **kwargs: json.dumps(result),
        runner.LaneFailure,
    )
    with pytest.raises(runner.LaneFailure, match="local-issuance-invalid-result"):
        instance.probe("issuance")


def test_local_cleanup_failure_preserves_primary_failure(
    checkout, tmp_path, fake_lane, monkeypatch
):
    def primary(*args):
        raise runner.LaneFailure("local-primary-failed")

    def cleanup(*args):
        raise runner.LaneFailure("local-secondary-failed")

    monkeypatch.setattr(runner.local.Runtime, "probe", primary)
    monkeypatch.setattr(runner.local.Runtime, "cleanup", cleanup)
    code, report = invoke(checkout, tmp_path)
    assert code == 1 and report["diagnostic"] == "local-primary-failed"
    assert report["stages"]["localCleanup"]["status"] == "failed"
    assert fake_lane[-1] == "cleanup"


def test_local_helper_cleanup_failure_still_attempts_teardown_and_volume(
    checkout, tmp_path
):
    calls = []

    def call(args, **kwargs):
        calls.append(args)
        if args[:3] == ["docker", "ps", "-aq"]:
            raise runner.LaneFailure("helper-list-failed")
        return ""

    instance = runner.local.Runtime(
        tmp_path / "local",
        checkout,
        runner.ROOT,
        "sdk-unique",
        "image",
        call,
        runner.LaneFailure,
    )
    with pytest.raises(runner.LaneFailure, match="helper-list-failed"):
        instance.cleanup()
    assert "down" in calls[-2]
    assert calls[-1] == ["docker", "volume", "rm", "sdk-unique-local-keys"]


def test_local_builds_actual_checkout_and_records_readiness_and_shutdown(
    checkout, tmp_path, fake_lane
):
    code, report = invoke(checkout, tmp_path)
    assert code == 0
    commands = [item[0] for item in fake_lane if isinstance(item, tuple)]
    assert [
        "mvn",
        "-B",
        "-ntp",
        "-f",
        str(checkout / "pom.xml"),
        "clean",
        "verify",
    ] in commands
    assert [
        "mvn",
        "-B",
        "-ntp",
        "-f",
        str(checkout / "sdks/java/pom.xml"),
        "clean",
        "install",
    ] in commands
    assert not any("loomspan-framework" in arg for args in commands for arg in args)
    assert (
        fake_lane.index("readiness")
        < fake_lane.index("startupFixture")
        < fake_lane.index("blockingClient")
        < fake_lane.index("fixture")
        < fake_lane.index("shutdown")
        < fake_lane.index("cleanup")
    )
    assert report["source"] == {"revision": "a" * 40, "dirty": True}
    assert report["frameworkVersion"] == "1.0.0-beta.8"
    assert (
        report["sidecarJarSha256"]
        == hashlib.sha256((checkout / "target/sidecar.jar").read_bytes()).hexdigest()
    )
    assert [artifact["coordinate"] for artifact in report["sdk"]] == [
        "ai.loomspan:loomspan-sdk-core:0.1.0-SNAPSHOT",
        "ai.loomspan:loomspan-sdk-spring-boot-starter:0.1.0-SNAPSHOT",
    ]
    assert all(value["status"] == "passed" for value in report["stages"].values())
    assert report["readiness"] == {"status": "UP"}
    assert report["shutdown"]["graceful"]
    assert report["startupFixture"] == {"modelRequests": 0}
    assert report["fixture"]["syntheticEffects"] == 1
    assert report["driver"]["sha256"]
    assert any("-Dsdk.version=0.1.0-SNAPSHOT" in args for args in commands)


@pytest.mark.parametrize("recipe", ["standard", "hardened"])
def test_remote_recipe_has_scenarios(checkout, tmp_path, monkeypatch, recipe):
    assert runner.RECIPES[recipe]


def test_unknown_recipe_is_usage_error():
    with pytest.raises(SystemExit) as error:
        runner.main(["unknown"])
    assert error.value.code == 2


@pytest.mark.parametrize(
    "phase",
    [
        "image_build",
        "start",
        "readiness",
        "startup_fixture",
        "blocking_client",
        "shutdown",
        "fixture",
        "deployment_transport",
        "cleanup",
    ],
)
def test_runtime_failure_cleanup_and_secret_free_report(
    checkout, tmp_path, fake_lane, monkeypatch, capsys, phase
):
    def fail(self):
        raise RuntimeError(" ".join(SENTINELS))

    monkeypatch.setattr(runner.Runtime, phase, fail)
    code, report = invoke(checkout, tmp_path)
    assert code == 1
    assert report["status"] == "failed"
    assert "cleanup" in fake_lane or phase == "cleanup"
    for sentinel in SENTINELS:
        assert sentinel not in json.dumps(report) + str(capsys.readouterr())


@pytest.mark.parametrize("interrupted", [False, True])
def test_primary_failure_survives_cleanup_failure(
    checkout, tmp_path, fake_lane, monkeypatch, interrupted
):
    def fail(self):
        if interrupted:
            raise KeyboardInterrupt()
        raise runner.LaneFailure("readiness-timeout")

    monkeypatch.setattr(runner.Runtime, "readiness", fail)
    monkeypatch.setattr(
        runner.Runtime,
        "cleanup",
        lambda self: (_ for _ in ()).throw(RuntimeError(" ".join(SENTINELS))),
    )
    code, report = invoke(checkout, tmp_path)
    assert code == 1
    assert report["diagnostic"] == (
        "interrupted" if interrupted else "readiness-timeout"
    )
    assert report["stages"]["cleanup"]["status"] == "failed"


@pytest.mark.parametrize("phase", ["preflight", "sidecarBuild", "sdkBuild"])
def test_build_failure_retains_failed_and_not_run_stages(
    checkout, tmp_path, fake_lane, monkeypatch, phase
):
    original = runner.command

    def command(args, **kwargs):
        args = list(map(str, args))
        hit = phase == "preflight" and args[:2] == ["docker", "info"]
        hit |= phase == "sidecarBuild" and args[-2:] == ["clean", "verify"]
        hit |= phase == "sdkBuild" and args[-2:] == ["clean", "install"]
        if hit:
            raise runner.LaneFailure("command-failed")
        return original(args, **kwargs)

    monkeypatch.setattr(runner, "command", command)
    code, report = invoke(checkout, tmp_path)
    assert code == 1
    assert report["stages"][phase]["status"] == "failed"
    assert report["stages"]["startup"]["status"] == "not-run"
    assert report["frameworkVersion"] is None


def test_missing_checkout_and_tools_are_reported(tmp_path, checkout, monkeypatch):
    code, report = invoke(tmp_path / "missing", tmp_path)
    assert code == 1
    assert report["diagnostic"] == "checkout-incomplete"
    assert report["source"]["revision"] is None
    monkeypatch.setattr(runner.shutil, "which", lambda tool: None)
    with pytest.raises(runner.LaneFailure, match="build-tool-unavailable"):
        runner.preflight(checkout)


@pytest.mark.parametrize(
    "versions", [[], ["1.0.0-beta.9"], ["1.0.0-beta.8", "1.0.0-beta.9"]]
)
def test_packaged_framework_identity_is_validated(checkout, versions):
    with zipfile.ZipFile(checkout / "target/sidecar.jar", "w") as archive:
        for version in versions:
            archive.writestr(
                f"BOOT-INF/lib/loomspan-spring-boot-starter-{version}.jar", b""
            )
    with pytest.raises(runner.LaneFailure, match="unexpected-framework-version"):
        runner.artifact_identity(checkout)


def test_missing_sdk_artifact_fails_with_report(checkout, tmp_path, fake_lane):
    next((checkout / "sdks/java/core/target").glob("*.jar")).unlink()
    code, report = invoke(checkout, tmp_path)
    assert code == 1
    assert report["stages"]["artifacts"]["status"] == "failed"
    assert report["diagnostic"] == "artifact-missing-or-ambiguous"


@pytest.mark.parametrize("failure", ["return", "timeout", "os"])
def test_command_suppresses_raw_diagnostics_and_environment(
    monkeypatch, capsys, failure
):
    monkeypatch.setenv("LOOMSPAN_OPENROUTER_API_KEY", SENTINELS[0])
    monkeypatch.setenv("JAVA_TOOL_OPTIONS", SENTINELS[1])
    monkeypatch.setenv("PROGRAMFILES", "C:/Program Files")
    monkeypatch.setenv("SYSTEMDRIVE", "C:")

    def run(args, **kwargs):
        assert not any(value in SENTINELS for value in kwargs["env"].values())
        assert kwargs["capture_output"] is True
        assert kwargs["env"]["PROGRAMFILES"] == "C:/Program Files"
        assert kwargs["env"]["SYSTEMDRIVE"] == "C:"
        if failure == "timeout":
            raise subprocess.TimeoutExpired(
                args, 1, output=SENTINELS[0], stderr=SENTINELS[1]
            )
        if failure == "os":
            raise OSError(SENTINELS[0])
        return SimpleNamespace(
            returncode=1, stdout=SENTINELS[0], stderr=" ".join(SENTINELS)
        )

    monkeypatch.setattr(runner.subprocess, "run", run)
    with pytest.raises(runner.LaneFailure) as error:
        runner.command(["mvn"])
    assert all(
        sentinel not in str(error.value) + str(capsys.readouterr())
        for sentinel in SENTINELS
    )


def runtime(monkeypatch, state=None):
    instance = runner.Runtime.__new__(runner.Runtime)
    instance.compose = ["docker", "compose", "-p", "sdk-test"]
    monkeypatch.setattr(instance, "container_state", lambda: state or {"Running": True})
    return instance


def test_readiness_polls_bounded_container_http_until_up(monkeypatch):
    instance = runtime(monkeypatch)
    responses = iter([None, "[]", '{"status":"UP"}'])

    def command(args, **kwargs):
        assert args[-1] == "http://localhost:8080/actuator/health/readiness"
        assert args[-3:-1] == ["--max-time", "2"]
        assert kwargs["timeout"] == 10
        response = next(responses)
        if response is None:
            raise runner.LaneFailure("command-failed")
        return response

    monkeypatch.setattr(runner, "command", command)
    monkeypatch.setattr(runner.time, "sleep", lambda seconds: None)
    assert instance.readiness() == {"status": "UP"}


def test_readiness_timeout_and_early_exit(monkeypatch):
    instance = runtime(monkeypatch)
    monkeypatch.setattr(runner, "command", lambda *args, **kwargs: "127.0.0.1:43210")
    clock = iter([0, 2])
    monkeypatch.setattr(runner.time, "monotonic", lambda: next(clock))
    with pytest.raises(runner.LaneFailure, match="readiness-timeout"):
        instance.readiness(timeout=1)
    monkeypatch.setattr(instance, "container_state", lambda: {"Running": False})
    monkeypatch.setattr(runner.time, "monotonic", lambda: 0)
    with pytest.raises(runner.LaneFailure, match="sidecar-exited-before-readiness"):
        instance.readiness()


@pytest.mark.parametrize(
    "exit_code,oom,marker,ok",
    [
        (0, False, True, True),
        (143, False, True, True),
        (137, False, True, False),
        (0, True, True, False),
        (0, False, False, False),
    ],
)
def test_shutdown_requires_normal_exit_and_graceful_completion(
    monkeypatch, exit_code, oom, marker, ok
):
    instance = runtime(
        monkeypatch,
        {"Running": False, "ExitCode": exit_code, "OOMKilled": oom, "Error": ""},
    )
    calls = []

    def command(args, **kwargs):
        calls.append(args)
        return ("Graceful shutdown complete" if marker else "") + " ".join(SENTINELS)

    monkeypatch.setattr(runner, "command", command)
    if ok:
        assert instance.shutdown()["graceful"]
    else:
        with pytest.raises(runner.LaneFailure, match="shutdown-not-graceful"):
            instance.shutdown()
    assert calls[0][-4:] == ["stop", "--timeout", "20", "sidecar"]


def test_compose_has_no_provider_or_retained_data_access(tmp_path):
    instance = runner.Runtime(tmp_path, tmp_path, "sdk-unique")
    compose = yaml.safe_load((runner.ROOT / "sdk/compose.yaml").read_bytes())
    assert compose["networks"]["sdk"]["internal"] is True
    assert all("ports" not in service for service in compose["services"].values())
    assert "/tmp:exec,mode=1777" in compose["services"]["sidecar"]["tmpfs"]
    for service in compose["services"].values():
        serialized = json.dumps(service)
        assert "docker.sock" not in serialized and ".runtime" not in serialized
        assert not any(
            "KEY" in name or "PASSWORD" in name
            for name in service.get("environment", {})
        )
    config = yaml.safe_load((tmp_path / "config/application.yaml").read_bytes())
    assert (
        config["loomspan"]["connections"]["fixture"]["base-url"]
        == "http://fixtures:8080/v1"
    )
    assert config["loomspan-sidecar"]["configuration"]["mode"] == "file"
    public = json.loads((tmp_path / "config/jwks.json").read_text())
    assert public["keys"][0]["kty"] == "RSA"
    assert instance.compose[instance.compose.index("-p") + 1] == "sdk-unique"
    assert set(path.name for path in (tmp_path / "config").iterdir()) == {
        "application.yaml",
        "jwks.json",
        "smoke.yaml",
        "sdkFailure.yaml",
        "sdkEffect.yaml",
        "routes.yaml",
    }
    token = (tmp_path / "credentials/execution.jwt").read_bytes()
    header, claims, signature = token.split(b".")

    def decode(value):
        return base64.urlsafe_b64decode(value + b"=" * (-len(value) % 4))

    claims = json.loads(decode(claims))
    assert claims["iss"] == "https://sdk.invalid"
    assert claims["aud"] == "sdk-smoke" and claims["exp"] > claims["iat"]
    assert "credentials" not in json.dumps(compose["services"]["sidecar"])
    assert "credentials" in json.dumps(compose["services"]["driver"])


def test_fixture_is_fixed_counts_requests_and_logs_no_input(capsys):
    server = FixtureServer(("127.0.0.1", 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with httpx.Client(trust_env=False, timeout=2) as client:
            assert client.get(base + "/counts").json() == {
                "modelRequests": 0,
                "syntheticEffects": 0,
                "submissionAttempts": 0,
                "forwardAttempts": 0,
            }
            response = client.post(
                base + "/v1/chat/completions",
                content=SENTINELS[2],
                headers={"Authorization": SENTINELS[0]},
            )
            assert (
                response.json()["choices"][0]["message"]["content"] == "fixture result"
            )
            assert client.get(base + "/counts").json()["modelRequests"] == 1
            assert (
                client.post(base + "/unknown", content=SENTINELS[2]).status_code == 404
            )
        assert all(value not in str(capsys.readouterr()) for value in SENTINELS)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_loss_proxy_forwards_once_drops_response_and_counts_effect_separately(capsys):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    fixture = FixtureServer(("127.0.0.1", 0))
    seen = []

    class Backend(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            seen.append(self.path)
            with httpx.Client(trust_env=False, timeout=2) as client:
                client.post(f"http://127.0.0.1:{fixture.server_port}/effect", json={})
            data = b'{"id":"27c186c5-6056-4de8-882d-60def5092909"}'
            self.send_response(202)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    backend = ThreadingHTTPServer(("127.0.0.1", 0), Backend)
    proxy = LossProxy(("127.0.0.1", 0), fixture, ("127.0.0.1", backend.server_port))
    servers = (fixture, backend, proxy)
    threads = [
        threading.Thread(target=server.serve_forever, daemon=True) for server in servers
    ]
    for thread in threads:
        thread.start()
    try:
        with httpx.Client(trust_env=False, timeout=2) as client:
            with pytest.raises(httpx.RemoteProtocolError):
                client.post(
                    f"http://127.0.0.1:{proxy.server_port}/v1/skills/sdkEffect/executions",
                    content=SENTINELS[2],
                    headers={"Authorization": SENTINELS[0]},
                )
            counts = client.get(f"http://127.0.0.1:{fixture.server_port}/counts").json()
            assert counts == {
                "modelRequests": 0,
                "syntheticEffects": 1,
                "submissionAttempts": 1,
                "forwardAttempts": 1,
            }
            assert (
                client.post(
                    f"http://127.0.0.1:{fixture.server_port}/fail", json={}
                ).status_code
                == 503
            )
            assert seen == ["/v1/skills/sdkEffect/executions"]
        assert all(value not in str(capsys.readouterr()) for value in SENTINELS)
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)


def test_driver_outcome_validation_and_bounded_effect_counts(monkeypatch):
    instance = runtime(monkeypatch)
    monkeypatch.setattr(runner, "command", lambda *args, **kwargs: '{"completed":true}')
    with pytest.raises(runner.LaneFailure, match="blocking-client-failed"):
        instance.blocking_client()
    monkeypatch.setattr(instance, "counts", lambda: {"modelRequests": 2})
    clock = iter([0, 11])
    monkeypatch.setattr(runner.time, "monotonic", lambda: next(clock))
    with pytest.raises(runner.LaneFailure, match="unexpected-fixture-counts"):
        instance.fixture()


def test_write_config_uses_current_jwks_execution_contract(tmp_path):
    config = tmp_path / "config"
    credentials = tmp_path / "credentials"
    config.mkdir()
    credentials.mkdir()
    runner.write_config(config, credentials)
    settings = yaml.safe_load((config / "application.yaml").read_bytes())[
        "loomspan-sidecar"
    ]
    assert settings["trust"] == {"mode": "file", "file": {"jwks": "/config/jwks.json"}}
    assert settings["auth"]["jwt"] == {"audience": "sdk-smoke"}
    (key,) = json.loads((config / "jwks.json").read_bytes())["keys"]
    assert key["kid"] and not ({"d", "p", "q", "dp", "dq", "qi"} & key.keys())
    parts = (credentials / "execution.jwt").read_bytes().split(b".")

    def decoded(value):
        return base64.urlsafe_b64decode(value + b"=" * (-len(value) % 4))

    from cryptography.hazmat.primitives.asymmetric import rsa

    public = rsa.RSAPublicNumbers(
        int.from_bytes(decoded(key["e"].encode())),
        int.from_bytes(decoded(key["n"].encode())),
    ).public_key()
    public.verify(
        decoded(parts[2]), b".".join(parts[:2]), padding.PKCS1v15(), hashes.SHA256()
    )
    header, claims = (json.loads(decoded(part)) for part in parts[:2])
    assert header == {
        "alg": "RS256",
        "typ": "loomspan-execution+jwt",
        "kid": key["kid"],
    }
    assert claims["token_use"] == "loomspan_execution"
    assert claims["iss"] and claims["sub"] and claims["aud"] == "sdk-smoke"
    assert 0 < claims["exp"] - claims["iat"] <= 600
    assert not list(config.glob("*.pem"))


@pytest.mark.parametrize("phase", ["shutdown_scenario", "deployment_transport"])
def test_new_scenario_failure_is_not_passing_evidence(
    checkout, tmp_path, fake_lane, monkeypatch, phase
):
    def fail(*args):
        raise runner.LaneFailure("baseline-failed")

    monkeypatch.setattr(runner.Runtime, phase, fail)
    code, report = invoke(checkout, tmp_path)
    assert code == 1 and report["diagnostic"] == "baseline-failed"
    assert "failed" in report["scenarioResults"].values()
    assert (
        "not-run" in report["scenarioResults"].values()
        or phase == "deployment_transport"
    )
    assert fake_lane[-1] == "cleanup"
    assert report["elapsedSeconds"] >= 0
    assert any(
        value["status"] == "failed" and value["elapsedSeconds"] >= 0
        for value in report["stages"].values()
    )


def test_shutdown_fixture_latch_sequences_nested_effects():
    server = FixtureServer(("127.0.0.1", 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors = []

    def identity():
        try:
            with httpx.Client(trust_env=False, timeout=5) as client:
                assert (
                    client.post(
                        f"http://127.0.0.1:{server.server_port}/callbacks/identity",
                        json={},
                    ).status_code
                    == 200
                )
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=identity)
    try:
        with httpx.Client(trust_env=False, timeout=3) as client:
            base = f"http://127.0.0.1:{server.server_port}"
            worker.start()
            assert server.entered.wait(2)
            assert worker.is_alive()
            assert client.get(base + "/shutdown/status").json() == {
                "entered": True,
                "detail": False,
                "finished": False,
            }
            assert client.post(base + "/shutdown/release", json={}).status_code == 200
            worker.join(timeout=3)
            assert not worker.is_alive() and not errors
            client.post(base + "/callbacks/detail", json={})
            for _ in range(4):
                assert (
                    client.post(base + "/planner/chat/completions", json={}).status_code
                    == 200
                )
            assert client.get(base + "/shutdown/status").json() == {
                "entered": True,
                "detail": True,
                "finished": True,
            }
            client.post(base + "/shutdown/reset", json={})
            assert client.get(base + "/shutdown/status").json() == {
                "entered": False,
                "detail": False,
                "finished": False,
            }
    finally:
        server.release.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_transport_rejection_does_not_accept_unavailable_service(monkeypatch):
    from sdk_lane import transport

    instance = SimpleNamespace(failure=runner.LaneFailure)
    instance.python = lambda *args: (_ for _ in ()).throw(
        runner.LaneFailure("command-failed")
    )
    with pytest.raises(runner.LaneFailure, match="command-failed"):
        transport.probe(instance, "sidecar", 8080, "wrong-ca")


def test_transport_certificates_are_public_trust_and_separate_expired_server(tmp_path):
    from sdk_lane import transport
    from cryptography import x509
    from datetime import datetime, timezone

    transport.certificates(tmp_path)
    ca = x509.load_pem_x509_certificate((tmp_path / "ca.pem").read_bytes())
    valid = x509.load_pem_x509_certificate((tmp_path / "valid.pem").read_bytes())
    expired = x509.load_pem_x509_certificate((tmp_path / "expired.pem").read_bytes())
    assert (
        valid.not_valid_after_utc
        > datetime.now(timezone.utc)
        > expired.not_valid_after_utc
    )
    for certificate in (valid, expired):
        ca.public_key().verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            padding.PKCS1v15(),
            certificate.signature_hash_algorithm,
        )
    assert not list(tmp_path.glob("*ca*key*"))


def test_shutdown_fixture_supplies_required_rest_target_contract(tmp_path, monkeypatch):
    instance = runner.Runtime(tmp_path, tmp_path, "sdk-fixture-contract")

    def stop_before_network(*args):
        raise runner.LaneFailure("fixture-prepared")

    monkeypatch.setattr(instance, "fixture_request", stop_before_network)
    with pytest.raises(runner.LaneFailure, match="fixture-prepared"):
        instance.shutdown_scenario(False)
    routes = yaml.safe_load((tmp_path / "config/routes.yaml").read_bytes())
    target = routes["targets"]["fixture"]
    assert target["connect-timeout"] == "2s"
    assert target["read-timeout"] == "20s"
    assert target["max-response-size"] == "16KB"
    assert {route["target"] for route in routes["routes"].values()} == {"fixture"}


@pytest.mark.parametrize(
    "label,host,trusted,expected",
    [
        ("valid", "sidecar", True, True),
        ("valid", "wrong.invalid", True, False),
        ("valid", "sidecar", False, False),
        ("expired", "sidecar", True, False),
    ],
)
def test_transport_material_passes_strict_tls_and_rejects_invalid_peers(
    tmp_path, label, host, trusted, expected
):
    import socket
    import ssl
    from sdk_lane import transport

    transport.certificates(tmp_path)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        str(tmp_path / f"{label}.pem"), str(tmp_path / f"{label}-key.pem")
    )
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(3)
    errors = []

    def accept():
        try:
            connection, _ = listener.accept()
            with connection:
                try:
                    with context.wrap_socket(connection, server_side=True) as stream:
                        stream.recv(1)
                except OSError:
                    pass
        except BaseException as error:
            errors.append(error)

    thread = threading.Thread(target=accept)
    thread.start()
    client = ssl.create_default_context(
        cafile=str(tmp_path / "ca.pem") if trusted else None
    )
    try:
        with socket.create_connection(listener.getsockname(), timeout=3) as raw:
            if expected:
                with client.wrap_socket(raw, server_hostname=host) as stream:
                    stream.sendall(b"x")
            else:
                with pytest.raises(ssl.SSLCertVerificationError):
                    client.wrap_socket(raw, server_hostname=host)
    finally:
        thread.join(timeout=3)
        listener.close()
    assert not errors and not thread.is_alive()


def test_callback_fixture_requires_admitted_model_barrier_then_emits_fixed_tool(capsys):
    fixture = LocalServer(("127.0.0.1", 0))
    thread = threading.Thread(target=fixture.serve_forever, daemon=True)
    thread.start()
    results = []
    errors = []
    base = f"http://127.0.0.1:{fixture.server_port}"

    def planning():
        try:
            with httpx.Client(trust_env=False, timeout=4) as client:
                results.append(
                    client.post(
                        base + "/callback/chat/completions", content=SENTINELS[2]
                    )
                )
        except BaseException as error:
            errors.append(type(error).__name__)

    worker = threading.Thread(target=planning)
    try:
        worker.start()
        assert fixture.entered.wait(2) and worker.is_alive()
        with httpx.Client(trust_env=False, timeout=3) as client:
            assert client.get(base + "/status").json() == {
                "entered": True,
                "models": 1,
                "effects": 0,
                "toolIssued": False,
            }
            client.post(base + "/release", json={})
            worker.join(timeout=3)
            assert not worker.is_alive() and not errors
            plan = json.loads(results[0].json()["choices"][0]["message"]["content"])
            assert [task["capabilityName"] for task in plan["tasks"]] == [
                "localExpiryOwned"
            ]
            response = client.post(base + "/callback/chat/completions", json={})
            action = json.loads(response.json()["choices"][0]["message"]["content"])
            assert action == {
                "stepAction": "CALL_TOOL",
                "taskId": "owned",
                "toolName": "localExpiryOwned",
                "toolArguments": {"message": "verify"},
            }
            assert client.get(base + "/status").json()["toolIssued"] is True
            # Extra turns cannot fabricate a successful response after child failure.
            assert (
                client.post(base + "/callback/chat/completions", json={}).status_code
                == 500
            )
            assert client.get(base + "/status").json()["effects"] == 0
            client.post(base + "/reset", json={})
            assert fixture.planner_step == 0 and not fixture.tool_issued
        assert all(
            value not in str(results) + str(capsys.readouterr()) for value in SENTINELS
        )
    finally:
        fixture.release.set()
        worker.join(timeout=2)
        fixture.shutdown()
        fixture.server_close()
        thread.join(timeout=2)


def test_callback_fixture_barrier_has_deadline(monkeypatch):
    fixture = LocalServer(("127.0.0.1", 0))
    deadlines = []
    monkeypatch.setattr(
        fixture.release, "wait", lambda timeout: deadlines.append(timeout) or False
    )
    thread = threading.Thread(target=fixture.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(trust_env=False, timeout=3) as client:
            response = client.post(
                f"http://127.0.0.1:{fixture.server_port}/callback/chat/completions",
                json={},
            )
            assert response.status_code == 504 and deadlines == [30]
        assert not fixture.tool_issued and fixture.effects == 0
    finally:
        fixture.shutdown()
        fixture.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize("name", ["callbacks", "callback-expiry"])
@pytest.mark.parametrize("mutation", ["missing", "false", "wrong-type", "unexpected"])
def test_callback_scenario_rejects_incomplete_or_inexact_evidence(
    checkout, tmp_path, name, mutation
):
    result = dict(runner.local.RESULTS[name])
    key = next(iter(result))
    if mutation == "missing":
        result.pop(key)
    elif mutation == "false":
        result[key] = False
    elif mutation == "wrong-type":
        result[key] = 1
    else:
        result["extra"] = True
    runtime = runner.local.Runtime(
        tmp_path / "local",
        checkout,
        runner.ROOT,
        "sdk-test",
        "image",
        lambda *args, **kwargs: json.dumps(result),
        runner.LaneFailure,
    )
    with pytest.raises(runner.LaneFailure, match="invalid-result"):
        runtime.probe(name)


def test_callback_configuration_fixes_destination_and_preserves_literal_role_admission(
    tmp_path,
):
    runner.local.configure(tmp_path / "config")
    routes = yaml.safe_load((tmp_path / "config/routes.yaml").read_bytes())
    assert routes["targets"]["app"]["base-url"] == "http://127.0.0.1:8081"
    assert routes["targets"]["app"]["auth"] == {"mode": "caller-passthrough"}
    for name in ("localOwned", "localLiteralOwned", "localExpiryOwned"):
        assert routes["routes"][name] == {
            "target": "app",
            "method": "POST",
            "path": "/loomspan/callbacks/owned",
        }
    literal = yaml.safe_load((tmp_path / "config/localLiteralOwned.yaml").read_bytes())
    assert literal["rbac_roles"] == ["ORDER_EDITOR"]
    planner = yaml.safe_load(
        (tmp_path / "config/localCallbackPlanner.yaml").read_bytes()
    )
    assert planner["planning_mode"] and planner["allowed_skills"] == [
        {"name": "localExpiryOwned"}
    ]
