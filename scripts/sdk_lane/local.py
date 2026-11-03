"""Compose the shipped colocated sample with the clean SDK servlet consumer."""

import copy
import hashlib
import json
import time

import yaml
from sdk_lane import outbound


SCENARIOS = (
    "local-issuance-roles",
    "local-ownership",
    "local-restart",
    "local-trust-recovery",
    "local-queue-expiry",
    "local-callback-authorization",
    "local-callback-expiry",
)
RESULTS = {
    "callbacks": {
        "forwardedIdentity": True,
        "credentialEqual": True,
        "methodDenied": True,
        "ownershipDenied": True,
        "formAndCsrfPreserved": True,
    },
    "callback-expiry": {
        "runningObserved": True,
        "plannerEntered": True,
        "exactChildFailure": True,
        "callbackArrivals": 0,
        "callbackBodies": 0,
        "callbackEffects": 0,
        "freshPolling": True,
    },
    "issuance": {
        "formLogin": True,
        "csrf": True,
        "exactRoles": True,
        "ownerFreshRead": True,
        "differentOwner404": True,
    },
    "restart": {"oldRejected": True, "newAccepted": True},
    "trust": {
        "readinessWithdrawn": True,
        "authenticationWithdrawn": True,
        "readinessRecovered": True,
        "authenticationRecovered": True,
    },
    "queue": {
        "queuedObserved": True,
        "expiredBeforeStart": True,
        "queuedEffects": 0,
        "freshPolling": True,
    },
}


def composition(checkout, root, config, image, volume):
    sample = checkout / "examples/quickstart/compose.yaml"
    source = sample.read_bytes()
    document = copy.deepcopy(yaml.safe_load(source))
    sidecar = document["services"]["sidecar"]
    inherited = {
        name: sidecar["environment"][name]
        for name in (
            "SERVER_ADDRESS",
            "LOOMSPAN_SIDECAR_TRUST_MODE",
            "LOOMSPAN_SIDECAR_TRUST_COLOCATED_KEY_DIRECTORY",
        )
    }
    sidecar["environment"] = inherited | {
        "SPRING_CONFIG_ADDITIONAL_LOCATION": "file:/config/application.yaml"
    }
    sidecar["image"] = image
    sidecar["volumes"] = [
        mount for mount in sidecar["volumes"] if mount.startswith("sidecar-keys:")
    ] + [f"{config.as_posix()}:/config:ro"]
    sidecar.pop("ports")
    sidecar["tmpfs"] = [
        "/sidecar/data:uid=10001,gid=10001,mode=0700",
        "/tmp:exec,mode=1777",
    ]
    sidecar["read_only"] = True
    sidecar["networks"] = ["sdk"]
    host = document["services"]["host"]
    host.pop("build")
    host.pop("healthcheck")
    host["image"] = "eclipse-temurin:21-jre"
    host["user"] = "10001:10001"
    host["environment"] = {}
    host["command"] = ["java", "-jar", "/app/reference.jar"]
    host["volumes"] += [
        f"{(root / 'sdk/reference-app/target/sdk-reference-app-0.1.0-SNAPSHOT.jar').as_posix()}:/app/reference.jar:ro"
    ]
    host["read_only"] = True
    host["tmpfs"] = ["/tmp:mode=1777"]
    document["services"] = {
        "sidecar": sidecar,
        "host": host,
        "fixtures": {
            "image": "python:3.13-slim",
            "network_mode": "service:sidecar",
            "depends_on": {"sidecar": {"condition": "service_started"}},
            "environment": {"SDK_LOCAL": "1", "PYTHONDONTWRITEBYTECODE": "1"},
            "command": ["python", "/fixture.py"],
            "read_only": True,
            "volumes": [
                f"{(root / 'scripts/sdk_lane/fixture.py').as_posix()}:/fixture.py:ro",
                f"{(root / 'scripts/sdk_lane/local_probe.py').as_posix()}:/probe.py:ro",
            ],
        },
    }
    document["volumes"] = {"sidecar-keys": {"external": True, "name": volume}}
    document["networks"] = {"sdk": {"internal": True}}
    return document, hashlib.sha256(source).hexdigest()


def configure(directory):
    directory.mkdir()
    for skill, model in (
        ("localModel", "normal"),
        ("localBlocker", "block"),
        ("localEffect", None),
        ("localOwned", None),
        ("localLiteralOwned", None),
        ("localExpiryOwned", None),
        ("localCallbackPlanner", "callback"),
    ):
        data = {
            "name": skill,
            "description": "Fixed Local fixture",
            "rbac_roles": ["ROLE_ORDER_EDITOR"],
            "input_schema": {"type": "object"},
        }
        if skill == "localExpiryOwned":
            data["input_schema"] = {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
                "additionalProperties": False,
            }
        if skill == "localLiteralOwned":
            data["rbac_roles"] = ["ORDER_EDITOR"]
        if skill == "localCallbackPlanner":
            data.update(
                planning_mode=True,
                concurrency=False,
                max_steps=3,
                allowed_skills=[{"name": "localExpiryOwned"}],
            )
        if model:
            data.update(model=model, prompt="Return fixture result")
        else:
            data["executor"] = "http"
            data["config"] = {"target": "fixture" if skill == "localEffect" else "app",
                "method": "POST", "path": "/effect" if skill == "localEffect" else "/loomspan/callbacks/owned"}
        (directory / (skill + ".yaml")).write_text(
            yaml.safe_dump(data), encoding="utf-8"
        )
    config = {
        "loomspan-sidecar": {
            "configuration": {"mode": "file"},
            "auth": {"jwt": {"audience": "loomspan-sidecar"}},
            "executions": {"max-concurrent": 1, "max-queued": 4},
        },
        "loomspan": {
            "executor-config": {"default": {"http": {"targets": {
                "app": {"base-url": "http://127.0.0.1:8081", "auth": {"mode": "caller-passthrough"},
                    "connect-timeout": "2s", "read-timeout": "3s", "max-response-size": "4KB"},
                "fixture": {"base-url": "http://127.0.0.1:8090", "auth": {"mode": "none"},
                    "connect-timeout": "2s", "read-timeout": "3s", "max-response-size": "1KB"}
            }}}},
            "connections": {},
            "models": {},
            "skills": {
                "locations": [
                    "file:/config/" + name + ".yaml"
                    for name in (
                        "localModel",
                        "localBlocker",
                        "localEffect",
                        "localOwned",
                        "localLiteralOwned",
                        "localExpiryOwned",
                        "localCallbackPlanner",
                    )
                ]
            },
            "observability": {"enabled": False},
        },
    }
    for model in ("normal", "block", "callback"):
        config["loomspan"]["connections"][model] = {
            "driver": "openai",
            "base-url": "http://127.0.0.1:8090/"
            + ("model" if model == "normal" else model),
            "api-key": "fixture-nonsecret",
            "provider-retry": {"max-attempts": 1},
            "request-timeout": "30s",
        }
        config["loomspan"]["models"][model] = {
            "connection": model,
            "provider-model": "fixture",
        }
    (directory / "application.yaml").write_text(
        yaml.safe_dump(config), encoding="utf-8"
    )


class Runtime:
    def __init__(
        self,
        directory,
        checkout,
        root,
        project,
        image,
        call,
        failure,
        outbound_only=False,
    ):
        self.call, self.failure = call, failure
        self.outbound_only = outbound_only
        self.project = project + ("-local-outbound" if outbound_only else "-local")
        self.volume = self.project + "-keys"
        self.image = image
        self.root = root
        directory.mkdir()
        config = directory / "config"
        configure(config)
        if outbound_only:
            outbound.configure(config)
        try:
            document, self.sample_hash = composition(
                checkout, root, config, image, self.volume
            )
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
            raise failure("local-sample-invalid") from None
        if outbound_only:
            outbound.adapt(document, root, "host")
        compose = directory / "compose.yaml"
        compose.write_text(yaml.safe_dump(document), encoding="utf-8")
        self.compose = ["docker", "compose", "-p", self.project, "-f", str(compose)]

    def start(self):
        self.call(
            [
                "docker",
                "volume",
                "create",
                "--label",
                "com.docker.compose.project=" + self.project,
                self.volume,
            ]
        )
        self.call(
            [
                "docker",
                "run",
                "--rm",
                "--label",
                "com.docker.compose.project=" + self.project,
                "--label",
                "loomspan.sdk.helper=" + self.project,
                "--user",
                "0:0",
                "-v",
                self.volume + ":/keys",
                "--entrypoint",
                "sh",
                self.image,
                "-c",
                "chown 10001:10001 /keys && chmod 0700 /keys",
            ],
            timeout=30,
        )
        self.call(self.compose + ["up", "-d"], timeout=180)
        if self.outbound_only:
            outbound.ready(self, "local", "fixtures")
        deadline = time.monotonic() + 120
        while not self.outbound_only:
            try:
                self.call(
                    self.compose
                    + [
                        "exec",
                        "-T",
                        "fixtures",
                        "python",
                        "-c",
                        "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/login',timeout=3); print('{}')",
                    ],
                    timeout=10,
                )
                break
            except self.failure:
                if time.monotonic() >= deadline:
                    raise self.failure("local-startup-timeout") from None
                time.sleep(0.25)
        # Separate readiness from app startup, which must export the initial JWKS.
        deadline = time.monotonic() + 30
        while True:
            try:
                value = json.loads(
                    self.call(
                        self.compose
                        + [
                            "exec",
                            "-T",
                            "sidecar",
                            "curl",
                            "--fail",
                            "--silent",
                            "--max-time",
                            "3",
                            "http://127.0.0.1:8080/actuator/health/readiness",
                        ],
                        timeout=10,
                    )
                )
                if value == {"status": "UP"}:
                    return
            except self.failure:
                pass
            if time.monotonic() >= deadline:
                raise self.failure("local-readiness-timeout")
            time.sleep(0.25)

    def probe(self, name):
        args = self.compose + ["exec", "-T", "fixtures", "python", "/probe.py", name]
        if name == "trust":
            container = self.call(self.compose + ["ps", "-q", "sidecar"]).strip()
            args = [
                "docker",
                "run",
                "--rm",
                "--label",
                "com.docker.compose.project=" + self.project,
                "--label",
                "loomspan.sdk.helper=" + self.project,
                "--user",
                "10001:10001",
                "--network",
                "container:" + container,
                "-v",
                self.volume + ":/keys",
                "-v",
                str(self.root / "scripts/sdk_lane/local_probe.py") + ":/probe.py:ro",
                "python:3.13-slim",
                "python",
                "/probe.py",
                name,
            ]
        try:
            result = json.loads(self.call(args, timeout=60))
        except Exception:
            raise self.failure("local-" + name + "-failed") from None
        if json.dumps(result, sort_keys=True) != json.dumps(
            RESULTS[name], sort_keys=True
        ):
            raise self.failure("local-" + name + "-invalid-result")
        return result

    def restart(self):
        started = time.monotonic()
        before = self.kid()
        self.call(self.compose + ["restart", "host"], timeout=90)
        deadline = time.monotonic() + 120
        while self.kid() == before:
            if time.monotonic() >= deadline:
                raise self.failure("local-key-not-replaced")
            time.sleep(0.1)
        # Wait for app listener independently, with no capture replacement.
        deadline = time.monotonic() + 30
        while True:
            try:
                self.call(
                    self.compose
                    + [
                        "exec",
                        "-T",
                        "fixtures",
                        "python",
                        "-c",
                        "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/login',timeout=3)",
                    ],
                    timeout=10,
                )
                break
            except self.failure:
                if time.monotonic() >= deadline:
                    raise self.failure("local-restart-timeout") from None
                time.sleep(0.1)
        result = self.probe("restart")
        if time.monotonic() - started >= 120:
            raise self.failure("local-restart-expiry-window-exceeded")
        return result | {"kidChanged": True, "beforeExpiry": True}

    def kid(self):
        # Only a public kid is observed; no token/private signer extraction.
        public = self.call(
            self.compose + ["exec", "-T", "host", "cat", "/keys/jwks.json"], timeout=10
        )
        return json.loads(public)["keys"][0]["kid"]

    def cleanup(self):
        try:
            try:
                helpers = (
                    self.call(
                        [
                            "docker",
                            "ps",
                            "-aq",
                            "--filter",
                            "label=loomspan.sdk.helper=" + self.project,
                        ]
                    )
                    or ""
                ).split()
                if helpers:
                    self.call(["docker", "rm", "--force", *helpers], timeout=30)
            finally:
                self.call(
                    self.compose
                    + ["down", "--timeout", "20", "--volumes", "--remove-orphans"],
                    timeout=90,
                )
        finally:
            self.call(["docker", "volume", "rm", self.volume], timeout=30)
