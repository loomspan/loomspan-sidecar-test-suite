"""Build the actual Sidecar/SDK checkout and run isolated SDK recipe scenarios."""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from xml.etree import ElementTree
import zipfile

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import yaml

from sdk_lane import local, remote, transport, outbound


ROOT = Path(__file__).resolve().parents[1]
RECIPES = {
    "local": [
        "foundation-smoke",
        "blocking-client",
        "shutdown-completion",
        "shutdown-cutoff",
        "deployment-transport-baseline",
        *local.SCENARIOS,
        "local-outbound-only",
    ],
    "standard": remote.scenarios("standard"),
    "hardened": remote.scenarios("hardened"),
}
STAGES = (
    "selection",
    "preflight",
    "sidecarBuild",
    "sdkBuild",
    "artifacts",
    "driverBuild",
    "referenceAppBuild",
    "imageBuild",
    "startup",
    "readiness",
    "startupFixture",
    "blockingClient",
    "shutdown",
    "fixture",
    "shutdownCompletion",
    "shutdownCutoff",
    "deploymentTransport",
    "localStartup",
    "localIssuance",
    "localRestart",
    "localTrust",
    "localQueue",
    "localCallbacks",
    "localCallbackExpiry",
    "localCleanup",
    "cleanup",
)


class LaneFailure(Exception):
    """Only fixed diagnostic categories cross into reports or terminal output."""


def child_environment():
    allowed = {
        "PATH",
        "SYSTEMROOT",
        "SYSTEMDRIVE",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "JAVA_HOME",
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "TEMP",
        "TMP",
        "DOCKER_CONFIG",
        "DOCKER_HOST",
        "DOCKER_CONTEXT",
        "PROGRAMFILES",
        "PROGRAMFILES(X86)",
        "PROGRAMDATA",
        "ALLUSERSPROFILE",
    }
    return {key: value for key, value in os.environ.items() if key.upper() in allowed}


def command(args, *, cwd=None, timeout=300):
    try:
        result = subprocess.run(
            [str(arg) for arg in args],
            cwd=cwd,
            env=child_environment(),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise LaneFailure("command-timeout") from None
    except OSError:
        raise LaneFailure("command-unavailable") from None
    if result.returncode:
        raise LaneFailure("command-failed")
    return result.stdout


def stage(report, name, action):
    scenario = {
        "shutdown": "foundation-smoke",
        "fixture": "blocking-client",
        "shutdownCompletion": "shutdown-completion",
        "shutdownCutoff": "shutdown-cutoff",
        "deploymentTransport": "deployment-transport-baseline",
        "localIssuance": "local-issuance-roles",
        "localRestart": "local-restart",
        "localTrust": "local-trust-recovery",
        "localQueue": "local-queue-expiry",
        "localCallbacks": "local-callback-authorization",
        "localCallbackExpiry": "local-callback-expiry",
    }.get(name)
    started = time.monotonic()
    report["stages"][name] = {"status": "running"}
    try:
        value = action()
    except BaseException:
        if scenario:
            report["scenarioResults"][scenario] = "failed"
        report["stages"][name] = {
            "status": "failed",
            "elapsedSeconds": round(time.monotonic() - started, 3),
        }
        raise
    report["stages"][name] = {
        "status": "passed",
        "elapsedSeconds": round(time.monotonic() - started, 3),
    }
    if scenario:
        report["scenarioResults"][scenario] = "passed"
    return value


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def revision(checkout):
    head = command(["git", "rev-parse", "HEAD"], cwd=checkout).strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", head):
        raise LaneFailure("invalid-source-identity")
    dirty = bool(command(["git", "status", "--porcelain"], cwd=checkout).strip())
    return {"revision": head, "dirty": dirty}


def find_jar(directory):
    jars = list(directory.glob("*.jar"))
    if len(jars) != 1:
        raise LaneFailure("artifact-missing-or-ambiguous")
    return jars[0]


def artifact_identity(checkout):
    jar = find_jar(checkout / "target")
    with zipfile.ZipFile(jar) as archive:
        pattern = r"BOOT-INF/lib/loomspan-spring-boot-starter-(.+)\.jar"
        versions = [
            match[1]
            for name in archive.namelist()
            if (match := re.fullmatch(pattern, name))
        ]
    if versions != ["1.0.0-beta.9-SNAPSHOT"]:
        raise LaneFailure("unexpected-framework-version")
    sdk = []
    for module in ("core", "spring-boot-starter"):
        built = find_jar(checkout / "sdks/java" / module / "target")
        with zipfile.ZipFile(built) as archive:
            names = [
                name for name in archive.namelist() if name.endswith("/pom.properties")
            ]
            if len(names) != 1:
                raise LaneFailure("invalid-sdk-metadata")
            properties = {}
            for line in archive.read(names[0]).decode().splitlines():
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    properties[key] = value
        expected = "loomspan-sdk-" + (
            "core" if module == "core" else "spring-boot-starter"
        )
        if (
            properties.get("groupId") != "ai.loomspan"
            or properties.get("artifactId") != expected
        ):
            raise LaneFailure("invalid-sdk-metadata")
        version = properties.get("version", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", version):
            raise LaneFailure("invalid-sdk-metadata")
        sdk.append(
            {"coordinate": f"ai.loomspan:{expected}:{version}", "sha256": digest(built)}
        )
    return jar, {
        "frameworkVersion": versions[0],
        "sidecarJarSha256": digest(jar),
        "sdk": sdk,
    }


def preflight(checkout):
    for name in ("pom.xml", "Dockerfile", "sdks/java/pom.xml"):
        if not (checkout / name).is_file():
            raise LaneFailure("checkout-incomplete")
    root = ElementTree.parse(checkout / "pom.xml").getroot()
    namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
    if (
        root.findtext("m:properties/m:loomspan.version", namespaces=namespace)
        != "1.0.0-beta.9-SNAPSHOT"
    ):
        raise LaneFailure("unexpected-framework-pin")
    maven = shutil.which("mvn")
    if not maven or not shutil.which("docker"):
        raise LaneFailure("build-tool-unavailable")
    command(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=30)
    command(["docker", "compose", "version"], timeout=30)
    return maven


def write_config(directory, credentials):
    # Private key lives only in memory; the token mount belongs to the driver alone.
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def encoded(value):
        return base64.urlsafe_b64encode(value).rstrip(b"=")

    numbers = private.public_key().public_numbers()

    def integer(value):
        return encoded(value.to_bytes((value.bit_length() + 7) // 8, "big")).decode()

    kid = "sdk-fixture"
    (directory / "jwks.json").write_text(
        json.dumps(
            {
                "keys": [
                    {
                        "kty": "RSA",
                        "kid": kid,
                        "alg": "RS256",
                        "use": "sig",
                        "n": integer(numbers.n),
                        "e": integer(numbers.e),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    now = int(time.time())
    claims = {
        "iss": "https://sdk.invalid",
        "sub": "sdk-driver",
        "aud": "sdk-smoke",
        "iat": now,
        "exp": now + 600,
        "roles": [],
        "token_use": "loomspan_execution",
    }
    signing_input = (
        encoded(
            json.dumps(
                {"alg": "RS256", "typ": "loomspan-execution+jwt", "kid": kid}
            ).encode()
        )
        + b"."
        + encoded(json.dumps(claims).encode())
    )
    token = (
        signing_input
        + b"."
        + encoded(private.sign(signing_input, padding.PKCS1v15(), hashes.SHA256()))
    )
    (credentials / "execution.jwt").write_bytes(token)
    (directory / "smoke.yaml").write_text(
        "name: sdkSmoke\ndescription: SDK startup fixture\nmodel: fixture\nprompt: Return fixture result\n",
        encoding="utf-8",
    )
    for name in ("sdkFailure", "sdkEffect"):
        (directory / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "description": "SDK deterministic HTTP fixture",
                    "executor": "http",
                    "config": {"target": "fixture", "method": "POST", "path": "/fail" if name == "sdkFailure" else "/effect"},
                    "input_schema": {"type": "object"},
                }
            ),
            encoding="utf-8",
        )
    config = {
        "loomspan-sidecar": {
            "configuration": {"mode": "file"},
            "trust": {"mode": "file", "file": {"jwks": "/config/jwks.json"}},
            "auth": {"jwt": {"audience": "sdk-smoke"}},
        },
        "loomspan": {
            "executor-config": {"default": {"http": {"targets": {"fixture": {
                "base-url": "http://fixtures:8080", "auth": {"mode": "none"},
                "connect-timeout": "2s", "read-timeout": "5s", "max-response-size": "1KB"
            }}}}},
            "connections": {
                "fixture": {
                    "driver": "openai",
                    "base-url": "http://fixtures:8080/v1",
                    "api-key": "sdk-fixture-nonsecret",
                    "provider-retry": {"max-attempts": 1},
                }
            },
            "models": {
                "fixture": {"connection": "fixture", "provider-model": "sdk-fixture"}
            },
            "skills": {
                "locations": [
                    "file:/config/smoke.yaml",
                    "file:/config/sdkFailure.yaml",
                    "file:/config/sdkEffect.yaml",
                ]
            },
            "observability": {"enabled": False},
            "shutdown": {"timeout": "5s"},
        },
        "server": {"shutdown": "graceful"},
        "spring": {"lifecycle": {"timeout-per-shutdown-phase": "5s"}},
    }
    (directory / "application.yaml").write_text(
        yaml.safe_dump(config), encoding="utf-8"
    )


class Runtime:
    def __init__(self, directory, checkout, project):
        self.directory = directory
        self.extra_compose = None
        self.failure = LaneFailure
        self.call = command
        self.project = project
        self.checkout = checkout
        self.image = f"loomspan-sdk-smoke:{project}"
        config = directory / "config"
        config.mkdir()
        credentials = directory / "credentials"
        credentials.mkdir()
        write_config(config, credentials)
        envfile = directory / "compose.env"
        envfile.write_text(
            f"SDK_IMAGE={self.image}\nSDK_CONFIG={config.as_posix()}\n"
            f"SDK_FIXTURE={(ROOT / 'scripts/sdk_lane/fixture.py').as_posix()}\n"
            f"SDK_DRIVER={(ROOT / 'sdk/driver/target').as_posix()}\n"
            f"SDK_CREDENTIALS={credentials.as_posix()}\n",
            encoding="utf-8",
        )
        self.compose = [
            "docker",
            "compose",
            "--project-directory",
            str(ROOT / "sdk"),
            "--env-file",
            str(envfile),
            "-p",
            project,
            "-f",
            str(ROOT / "sdk/compose.yaml"),
        ]

    def python(self, service, script, service_python=True):
        compose = self.extra_compose or self.compose
        if service_python:
            args = compose + ["exec", "-T", service, "python", "-c", script]
        else:
            args = compose + [
                "run",
                "--rm",
                "--no-deps",
                "-T",
                "--entrypoint",
                "python",
                "fixtures",
                "-c",
                script,
            ]
        return json.loads(command(args, timeout=30))

    def fixture_request(self, path, post=False):
        return self.python(
            "fixtures",
            "import urllib.request,json; print(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8080"
            + path
            + "', data="
            + ("b'{}'" if post else "None")
            + "), timeout=3).read().decode())",
        )

    def shutdown_scenario(self, cutoff):
        config = self.directory / "config"
        settings = yaml.safe_load((config / "application.yaml").read_bytes())
        settings["loomspan"]["shutdown"]["timeout"] = "3s"
        settings["loomspan"]["connections"]["fixture"]["base-url"] = (
            "http://fixtures:8080/planner"
        )
        settings["loomspan"]["skills"]["locations"] = [
            "file:/config/planner.yaml",
            "file:/config/identity.yaml",
            "file:/config/detail.yaml",
        ]
        (config / "application.yaml").write_text(
            yaml.safe_dump(settings), encoding="utf-8"
        )
        planner = {
            "name": "shutdownPlanner",
            "description": "Deterministic nested shutdown work",
            "model": "fixture",
            "planning_mode": True,
            "concurrency": False,
            "max_steps": 4,
            "allowed_skills": [{"name": "identityLeaf"}, {"name": "detailLeaf"}],
            "input_schema": {"type": "object"},
        }
        (config / "planner.yaml").write_text(yaml.safe_dump(planner), encoding="utf-8")
        settings["loomspan"]["executor-config"]["default"]["http"]["targets"]["fixture"]["read-timeout"] = "20s"
        settings["loomspan"]["executor-config"]["default"]["http"]["targets"]["fixture"]["max-response-size"] = "16KB"
        (config / "application.yaml").write_text(yaml.safe_dump(settings), encoding="utf-8")
        for name in ("identity", "detail"):
            (config / f"{name}.yaml").write_text(
                yaml.safe_dump(
                    {
                        "name": name + "Leaf",
                        "description": "Nested fixture",
                        "executor": "http",
                        "config": {"target": "fixture", "method": "POST", "path": "/callbacks/" + name},
                        "input_schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    }
                ),
                encoding="utf-8",
            )
        self.fixture_request("/shutdown/reset", True)
        command(self.compose + ["up", "-d", "--force-recreate", "sidecar"], timeout=180)
        self.readiness()
        # Token read inside this disposable client; it never appears in command arguments.
        script = "import urllib.request,json; token=open('/credentials/execution.jwt').read(); request=urllib.request.Request('http://sidecar:8080/v1/skills/shutdownPlanner/executions',data=b'{}',headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}); response=urllib.request.urlopen(request,timeout=5); assert response.status == 202; print('{}')"
        command(
            self.compose
            + [
                "run",
                "--rm",
                "--no-deps",
                "-T",
                "-v",
                str(self.directory / "credentials") + ":/credentials:ro",
                "--entrypoint",
                "python",
                "fixtures",
                "-c",
                script,
            ],
            timeout=30,
        )
        deadline = time.monotonic() + 20
        while not self.fixture_request("/shutdown/status")["entered"]:
            if time.monotonic() >= deadline:
                raise LaneFailure("shutdown-work-not-entered")
            time.sleep(0.05)
        container = command(self.compose + ["ps", "-q", "sidecar"]).strip()
        started = time.monotonic()
        command(["docker", "kill", "--signal=TERM", container], timeout=10)
        time.sleep(0.3)
        if not self.container_state().get("Running"):
            raise LaneFailure("shutdown-premature-exit")
        if not cutoff:
            self.fixture_request("/shutdown/release", True)
        command(["docker", "wait", container], timeout=15)
        elapsed = time.monotonic() - started
        state = self.container_state()
        progress = self.fixture_request("/shutdown/status")
        if (
            state.get("Running")
            or state.get("ExitCode") not in (0, 143)
            or state.get("OOMKilled")
            or state.get("Error")
            or elapsed >= 12
        ):
            raise LaneFailure("shutdown-process-failed")
        if cutoff:
            if elapsed < 2.5 or progress["detail"] or progress["finished"]:
                raise LaneFailure("shutdown-cutoff-failed")
        elif not progress["detail"] or not progress["finished"]:
            raise LaneFailure("shutdown-completion-failed")
        return {
            "elapsedSeconds": round(elapsed, 3),
            "exitCode": state["ExitCode"],
            "oomKilled": False,
            **progress,
        }

    def deployment_transport(self):
        return transport.run(self)

    def image_build(self):
        command(
            ["docker", "build", "--tag", self.image, str(self.checkout)], timeout=600
        )

    def start(self):
        command(self.compose + ["up", "-d"], timeout=180)

    def container_state(self):
        container = command(self.compose + ["ps", "--all", "-q", "sidecar"]).strip()
        if not re.fullmatch(r"[0-9a-f]{12,64}", container):
            raise LaneFailure("sidecar-container-missing")
        value = command(["docker", "inspect", "--format", "{{json .State}}", container])
        return json.loads(value)

    def readiness(self, timeout=120):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.container_state().get("Running"):
                raise LaneFailure("sidecar-exited-before-readiness")
            try:
                raw = command(
                    self.compose
                    + [
                        "exec",
                        "-T",
                        "sidecar",
                        "curl",
                        "--fail",
                        "--silent",
                        "--max-time",
                        "2",
                        "http://localhost:8080/actuator/health/readiness",
                    ],
                    timeout=10,
                )
                if json.loads(raw) == {"status": "UP"}:
                    return {"status": "UP"}
            except (LaneFailure, ValueError, AttributeError):
                pass
            time.sleep(1)
        raise LaneFailure("readiness-timeout")

    def shutdown(self):
        command(self.compose + ["stop", "--timeout", "20", "sidecar"], timeout=30)
        state = self.container_state()
        logs = command(self.compose + ["logs", "--no-color", "sidecar"])
        normal = (
            not state.get("Running")
            and state.get("ExitCode") in (0, 143)
            and not state.get("OOMKilled")
            and not state.get("Error")
            and "Graceful shutdown complete" in logs
        )
        if not normal:
            raise LaneFailure("shutdown-not-graceful")
        return {"exitCode": state["ExitCode"], "graceful": True, "oomKilled": False}

    def counts(self):
        raw = command(
            self.compose
            + [
                "exec",
                "-T",
                "fixtures",
                "python",
                "-c",
                "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/counts', timeout=2).read().decode())",
            ]
        )
        return json.loads(raw)

    def startup_fixture(self):
        count = self.counts().get("modelRequests")
        if type(count) is not int or count != 0:
            raise LaneFailure("unexpected-model-requests")
        return {"modelRequests": count}

    def blocking_client(self):
        raw = command(
            self.compose + ["run", "--rm", "--no-deps", "-T", "driver"], timeout=90
        )
        try:
            outcomes = json.loads(raw)
        except ValueError:
            raise LaneFailure("invalid-driver-report") from None
        expected = {
            "completed",
            "opaqueResultPreserved",
            "failed",
            "primaryFailurePreserved",
            "acceptanceUnknown",
        }
        if (
            not isinstance(outcomes, dict)
            or set(outcomes) != expected
            or any(value is not True for value in outcomes.values())
        ):
            raise LaneFailure("blocking-client-failed")
        return outcomes

    def fixture(self):
        expected = {
            "modelRequests": 1,
            "syntheticEffects": 1,
            "submissionAttempts": 1,
            "forwardAttempts": 1,
        }
        deadline = time.monotonic() + 10
        while True:
            counts = self.counts()
            if counts == expected:
                break
            if time.monotonic() >= deadline:
                raise LaneFailure("unexpected-fixture-counts")
            time.sleep(0.1)
        time.sleep(0.3)
        if self.counts() != expected:
            raise LaneFailure("unexpected-fixture-counts")
        return expected

    def cleanup(self):
        command(
            (self.extra_compose or self.compose)
            + ["down", "--timeout", "20", "--volumes", "--remove-orphans"],
            timeout=90,
        )


def write_report(directory, report):
    temporary = directory / "report.json.tmp"
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(directory / "report.json")


def build_checkout(report, checkout):
    def prepare():
        maven = preflight(checkout)
        report["source"] = revision(checkout)
        report["suiteSource"] = revision(ROOT)
        return maven

    maven = stage(report, "preflight", prepare)
    base = [maven, "-B", "-ntp", "-f"]
    stage(
        report,
        "sidecarBuild",
        lambda: command(
            base + [checkout / "pom.xml", "clean", "verify"],
            cwd=checkout,
            timeout=900,
        ),
    )
    stage(
        report,
        "sdkBuild",
        lambda: command(
            base + [checkout / "sdks/java/pom.xml", "clean", "install"],
            cwd=checkout,
            timeout=300,
        ),
    )
    _, identity = stage(report, "artifacts", lambda: artifact_identity(checkout))
    report.update(identity)

    def driver_build():
        coordinate = identity["sdk"][0]["coordinate"]
        version = coordinate.rsplit(":", 1)[1]
        command(
            base
            + [
                ROOT / "sdk/driver/pom.xml",
                f"-Dsdk.version={version}",
                "clean",
                "package",
            ],
            cwd=ROOT,
            timeout=300,
        )
        return {"sha256": digest(find_jar(ROOT / "sdk/driver/target"))}

    report["driver"] = stage(report, "driverBuild", driver_build)

    def reference_build():
        version = identity["sdk"][0]["coordinate"].rsplit(":", 1)[1]
        command(
            base
            + [
                ROOT / "sdk/reference-app/pom.xml",
                f"-Dsdk.version={version}",
                "clean",
                "package",
            ],
            cwd=ROOT,
            timeout=300,
        )
        return {"sha256": digest(find_jar(ROOT / "sdk/reference-app/target"))}

    report["referenceApp"] = stage(report, "referenceAppBuild", reference_build)


def run_smoke(report, checkout, directory):
    runtime = Runtime(directory, checkout, "sdk-" + uuid.uuid4().hex[:16])
    try:
        stage(report, "imageBuild", runtime.image_build)
        stage(report, "startup", runtime.start)
        report["readiness"] = stage(report, "readiness", runtime.readiness)
        report["startupFixture"] = stage(
            report, "startupFixture", runtime.startup_fixture
        )
        report["blockingClient"] = stage(
            report, "blockingClient", runtime.blocking_client
        )
        report["fixture"] = stage(report, "fixture", runtime.fixture)
        report["shutdown"] = stage(report, "shutdown", runtime.shutdown)
        report["shutdownCompletion"] = stage(
            report, "shutdownCompletion", lambda: runtime.shutdown_scenario(False)
        )
        report["shutdownCutoff"] = stage(
            report, "shutdownCutoff", lambda: runtime.shutdown_scenario(True)
        )
        report["deploymentTransport"] = stage(
            report, "deploymentTransport", runtime.deployment_transport
        )
        local_runtime = local.Runtime(
            directory / "local",
            checkout,
            ROOT,
            runtime.project,
            runtime.image,
            command,
            LaneFailure,
        )
        report["localRecipe"] = {
            "sampleSha256": local_runtime.sample_hash,
            "project": local_runtime.project,
            "keyVolume": local_runtime.volume,
        }
        local_failure = None
        try:
            stage(report, "localStartup", local_runtime.start)
            report["localRecipe"]["issuance"] = stage(
                report, "localIssuance", lambda: local_runtime.probe("issuance")
            )
            report["scenarioResults"]["local-ownership"] = "passed"
            report["localRecipe"]["restart"] = stage(
                report, "localRestart", local_runtime.restart
            )
            report["localRecipe"]["trust"] = stage(
                report, "localTrust", lambda: local_runtime.probe("trust")
            )
            report["localRecipe"]["queue"] = stage(
                report, "localQueue", lambda: local_runtime.probe("queue")
            )
            report["localRecipe"]["callbacks"] = stage(
                report, "localCallbacks", lambda: local_runtime.probe("callbacks")
            )
            report["localRecipe"]["callbackExpiry"] = stage(
                report,
                "localCallbackExpiry",
                lambda: local_runtime.probe("callback-expiry"),
            )
        except BaseException as failure:
            local_failure = failure
            raise
        finally:
            try:
                stage(report, "localCleanup", local_runtime.cleanup)
            except Exception:
                if local_failure is None:
                    raise LaneFailure("local-cleanup-failed") from None
        only = local.Runtime(
            directory / "outbound",
            checkout,
            ROOT,
            runtime.project,
            runtime.image,
            command,
            LaneFailure,
            outbound_only=True,
        )
        report["outboundOnly"] = {"project": only.project, "keyVolume": only.volume}
        primary = None
        try:
            stage(report, "localOutboundStartup", only.start)
            report["outboundOnly"]["observations"] = stage(
                report, "localOutbound", lambda: outbound.run(only, "local")
            )
            report["scenarioResults"]["local-outbound-only"] = "passed"
        except BaseException as failure:
            primary = failure
            report["scenarioResults"]["local-outbound-only"] = "failed"
            raise
        finally:
            try:
                stage(report, "localOutboundCleanup", only.cleanup)
            except Exception:
                report["scenarioResults"]["local-outbound-only"] = "failed"
                if primary is None:
                    raise LaneFailure("outbound-cleanup-failed") from None
        if any(value != "passed" for value in report["scenarioResults"].values()):
            raise LaneFailure("incomplete-scenario-results")
        report["status"] = "passed"
    finally:
        try:
            stage(report, "cleanup", runtime.cleanup)
        except Exception:
            # Preserve the primary failure; cleanup failure always fails the run.
            if report["status"] == "passed":
                report["diagnostic"] = "cleanup-failed"
            report["status"] = "failed"


def run_remote(report, checkout, directory):
    project = "sdk-" + uuid.uuid4().hex[:16]
    image = "loomspan-sdk-smoke:" + project
    stage(
        report,
        "imageBuild",
        lambda: command(["docker", "build", "-t", image, str(checkout)], timeout=300),
    )
    report["remoteRecipe"] = {"projects": [], "results": {}}
    for variant in remote.VARIANTS[report["recipe"]]:
        scenario = report["recipe"] + "-" + variant
        runtime = remote.Runtime(
            directory / variant,
            checkout,
            ROOT,
            project,
            image,
            report["recipe"],
            variant,
            command,
            LaneFailure,
        )
        report["remoteRecipe"]["projects"].append(
            {"project": runtime.project, "publicVolume": runtime.volume}
        )
        primary = None
        try:
            stage(report, scenario + "-startup", runtime.start)
            result = stage(report, scenario, runtime.run)
            if json.dumps(result, sort_keys=True) != json.dumps(
                remote.observations(report["recipe"], variant, "scenario")
                if variant != "isolation"
                else {"passed": True},
                sort_keys=True,
            ):
                raise LaneFailure("remote-invalid-result")
            report["remoteRecipe"]["results"][scenario] = result
            report["scenarioResults"][scenario] = "passed"
        except BaseException as failure:
            primary = failure
            report["scenarioResults"][scenario] = "failed"
            raise
        finally:
            try:
                stage(report, scenario + "-cleanup", runtime.cleanup)
            except Exception:
                report["scenarioResults"][scenario] = "failed"
                if primary is None:
                    raise LaneFailure("remote-cleanup-failed") from None
    if any(value != "passed" for value in report["scenarioResults"].values()):
        raise LaneFailure("incomplete-scenario-results")
    report["status"] = "passed"


def main(argv=None):
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", choices=RECIPES)
    parser.add_argument(
        "--sidecar-checkout", type=Path, default=ROOT.parent / "loomspan-sidecar"
    )
    parser.add_argument(
        "--output", type=Path, help="New directory for this run's report"
    )
    args = parser.parse_args(argv)
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:12]
    )
    output = args.output or ROOT / "evidence/sdk" / run_id
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "runId": run_id,
        "recipe": args.recipe,
        "scenarios": RECIPES[args.recipe],
        "scenarioResults": {name: "not-run" for name in RECIPES[args.recipe]},
        "status": "failed",
        "source": {"revision": None, "dirty": None},
        "suiteSource": {"revision": None, "dirty": None},
        "frameworkVersion": None,
        "sidecarJarSha256": None,
        "sdk": None,
        "driver": None,
        "referenceApp": None,
        "localRecipe": None,
        "readiness": None,
        "startupFixture": None,
        "blockingClient": None,
        "shutdown": None,
        "fixture": None,
        "stages": {name: {"status": "not-run"} for name in STAGES},
        "diagnostic": None,
    }
    write_report(output, report)
    try:
        with tempfile.TemporaryDirectory(prefix="loomspan-sdk-") as temporary:

            def select():
                if not RECIPES[args.recipe]:
                    raise LaneFailure("no-scenarios-for-recipe")

            stage(report, "selection", select)
            checkout = args.sidecar_checkout.resolve()
            build_checkout(report, checkout)
            if args.recipe == "local":
                run_smoke(report, checkout, Path(temporary))
            else:
                run_remote(report, checkout, Path(temporary))
    except LaneFailure as failure:
        report["status"] = "failed"
        report["diagnostic"] = str(failure)
    except KeyboardInterrupt:
        report["status"] = "failed"
        report["diagnostic"] = "interrupted"
    except Exception:
        report["status"] = "failed"
        report["diagnostic"] = "unexpected-error"
    finally:
        report["elapsedSeconds"] = round(time.monotonic() - started, 3)
        write_report(output, report)
    summary = report["diagnostic"] or (
        "foundation-smoke" if args.recipe == "local" else "remote-recipes"
    )
    print(f"SDK {args.recipe}: {report['status']} ({summary}).")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
