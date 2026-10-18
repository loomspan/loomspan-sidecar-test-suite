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
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


import run_sdk as runner
from sdk_lane.fixture import FixtureServer, LossProxy


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
    monkeypatch.setattr(
        runner,
        "find_jar",
        lambda directory: driver
        if directory == runner.ROOT / "sdk/driver/target"
        else original_find(directory),
    )

    class Runtime:
        def __init__(self, directory, checkout, project):
            assert project.startswith("sdk-")

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

        def cleanup(self):
            calls.append("cleanup")

    monkeypatch.setattr(runner, "Runtime", Runtime)
    return calls


def invoke(checkout, tmp_path, recipe="local"):
    output = tmp_path / "report"
    code = runner.main(
        [recipe, "--sidecar-checkout", str(checkout), "--output", str(output)]
    )
    return code, json.loads((output / "report.json").read_bytes())


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
def test_empty_recipes_fail_before_builds_with_durable_evidence(
    checkout, tmp_path, monkeypatch, recipe
):
    monkeypatch.setattr(
        runner, "preflight", lambda *args: pytest.fail("empty recipe must not build")
    )
    code, report = invoke(checkout, tmp_path, recipe)
    assert code == 1
    assert report["recipe"] == recipe
    assert report["diagnostic"] == "no-scenarios-for-recipe"
    assert report["scenarios"] == []
    assert report["stages"]["selection"]["status"] == "failed"
    assert all(
        report["stages"][name]["status"] == "not-run" for name in runner.STAGES[1:]
    )


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
        assert args[-1] == "http://localhost:9091/actuator/health/readiness"
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
    public = (tmp_path / "config/jwt-public.pem").read_text()
    assert "PUBLIC KEY" in public and "PRIVATE KEY" not in public
    assert instance.compose[instance.compose.index("-p") + 1] == "sdk-unique"
    assert set(path.name for path in (tmp_path / "config").iterdir()) == {
        "application.yaml",
        "jwt-public.pem",
        "smoke.yaml",
        "sdkFailure.yaml",
        "sdkEffect.yaml",
        "routes.yaml",
    }
    token = (tmp_path / "credentials/execution.jwt").read_bytes()
    header, claims, signature = token.split(b".")

    def decode(value):
        return base64.urlsafe_b64decode(value + b"=" * (-len(value) % 4))

    public_key = serialization.load_pem_public_key(public.encode())
    public_key.verify(
        decode(signature), header + b"." + claims, padding.PKCS1v15(), hashes.SHA256()
    )
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
