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

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import yaml


ROOT = Path(__file__).resolve().parents[1]
RECIPES = {
    "local": ["foundation-smoke", "blocking-client"],
    "standard": [],
    "hardened": [],
}
STAGES = (
    "selection",
    "preflight",
    "sidecarBuild",
    "sdkBuild",
    "artifacts",
    "driverBuild",
    "imageBuild",
    "startup",
    "readiness",
    "startupFixture",
    "blockingClient",
    "shutdown",
    "fixture",
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
    report["stages"][name] = {"status": "running"}
    try:
        value = action()
    except BaseException:
        report["stages"][name] = {"status": "failed"}
        raise
    report["stages"][name] = {"status": "passed"}
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
    if versions != ["1.0.0-beta.8"]:
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
        != "1.0.0-beta.8"
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
    public = private.public_key()
    (directory / "jwt-public.pem").write_bytes(
        public.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    def encoded(value):
        return base64.urlsafe_b64encode(value).rstrip(b"=")

    now = int(time.time())
    claims = {
        "iss": "https://sdk.invalid",
        "sub": "sdk-driver",
        "aud": "sdk-smoke",
        "iat": now,
        "exp": now + 600,
        "roles": [],
    }
    signing_input = (
        encoded(b'{"alg":"RS256","typ":"JWT"}')
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
                    "description": "SDK deterministic REST fixture",
                    "rest": True,
                    "input_schema": {"type": "object"},
                }
            ),
            encoding="utf-8",
        )
    (directory / "routes.yaml").write_text(
        yaml.safe_dump(
            {
                "targets": {
                    "fixture": {
                        "base-url": "http://fixtures:8080",
                        "auth": {"mode": "none"},
                        "connect-timeout": "2s",
                        "read-timeout": "5s",
                        "max-response-size": "1KB",
                    }
                },
                "routes": {
                    "sdkFailure": {
                        "target": "fixture",
                        "method": "POST",
                        "path": "/fail",
                    },
                    "sdkEffect": {
                        "target": "fixture",
                        "method": "POST",
                        "path": "/effect",
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    config = {
        "loomspan-sidecar": {
            "configuration": {"mode": "file"},
            "rest-routes": {"location": "file:/config/routes.yaml"},
            "auth": {
                "jwt": {
                    "issuer-uri": "https://sdk.invalid",
                    "audience": "sdk-smoke",
                    "public-key-location": "file:/config/jwt-public.pem",
                }
            },
        },
        "loomspan": {
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
                        "http://localhost:9091/actuator/health/readiness",
                    ],
                    timeout=10,
                )
                if json.loads(raw).get("status") == "UP":
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
            self.compose + ["down", "--timeout", "20", "--remove-orphans"], timeout=60
        )


def write_report(directory, report):
    temporary = directory / "report.json.tmp"
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(directory / "report.json")


def build_checkout(report, checkout):
    def prepare():
        maven = preflight(checkout)
        report["source"] = revision(checkout)
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
        report["status"] = "passed"
    finally:
        try:
            stage(report, "cleanup", runtime.cleanup)
        except Exception:
            # Preserve the primary failure; cleanup failure always fails the run.
            if report["status"] == "passed":
                report["diagnostic"] = "cleanup-failed"
            report["status"] = "failed"


def main(argv=None):
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
        "status": "failed",
        "source": {"revision": None, "dirty": None},
        "frameworkVersion": None,
        "sidecarJarSha256": None,
        "sdk": None,
        "driver": None,
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
            run_smoke(report, checkout, Path(temporary))
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
        write_report(output, report)
    print(
        f"SDK {args.recipe}: {report['status']} ({report['diagnostic'] or 'foundation-smoke'})."
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
