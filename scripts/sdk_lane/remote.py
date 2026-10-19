"""Two bounded remote deployments. Recipe names never enter application contracts."""

import copy
import base64
import json
import time

import yaml
from cryptography import x509

from sdk_lane import local, remote_material
from sdk_lane.remote_contract import observations


VARIANTS = {
    "standard": (
        "positive",
        "invocation-server",
        "callback-host",
        "callback-expired",
        "submission-loss",
        "callback-loss",
    ),
    "hardened": (
        "positive",
        "invocation-client",
        "invocation-server",
        "callback-client",
        "callback-server",
        "isolation",
        "submission-loss",
        "callback-loss",
    ),
}


def scenarios(recipe):
    return [recipe + "-" + variant for variant in VARIANTS[recipe]]


def dump(path, value):
    path.write_text(yaml.safe_dump(value), encoding="utf-8")


def configure(directory, checkout, recipe, variant):
    """Overlay supplied operator fragments with only fixture paths and endpoints."""
    directory.mkdir()
    local.configure(directory / "sidecar")
    base = checkout / "examples/remote" / recipe
    app = yaml.safe_load((base / "app.yaml").read_text())
    sidecar = yaml.safe_load((base / "sidecar.yaml").read_text())
    fixture = yaml.safe_load((directory / "sidecar/application.yaml").read_text())
    fixture["server"] = sidecar["server"]
    fixture["spring"] = sidecar.get("spring", {})
    fixture["loomspan-sidecar"]["trust"] = sidecar["loomspan-sidecar"]["trust"]
    routes = yaml.safe_load((directory / "sidecar/routes.yaml").read_text())
    routes["targets"]["app"] = yaml.safe_load((base / "rest-routes.yaml").read_text())[
        "targets"
    ]["app"]
    if recipe == "standard":
        server = "wrong-ca-server" if variant == "invocation-server" else "server"
        fixture["server"]["ssl"]["certificate"] = "file:/tls/sidecar-" + server + ".pem"
        fixture["server"]["ssl"]["certificate-private-key"] = (
            "file:/tls/sidecar-" + server + "-key.pem"
        )
        server = {"callback-host": "wrong-host", "callback-expired": "expired"}.get(
            variant, "server"
        )
        app["server"]["ssl"]["certificate"] = "file:/tls/app-" + server + ".pem"
        app["server"]["ssl"]["certificate-private-key"] = (
            "file:/tls/app-" + server + "-key.pem"
        )
    app["logging"] = {"level": {"root": "WARN"}}
    app["loomspan-sdk"]["issuance"] = {
        "issuer": "loomspan-app",
        "lifetime": "5m",
        "roles": ["ROLE_ORDER_EDITOR", "ORDER_EDITOR"],
    }
    app["loomspan-sdk"]["response-timeout"] = "3s"
    if variant == "submission-loss" and recipe == "standard":
        app["loomspan-sdk"]["base-url"] = "https://sidecar:9443"
    if variant == "callback-loss" and recipe == "standard":
        routes["targets"]["app"]["base-url"] = "https://app:9443"
    dump(directory / "app.yaml", app)
    dump(directory / "sidecar/application.yaml", fixture)
    dump(directory / "sidecar/routes.yaml", routes)
    if recipe == "hardened":
        for peer in ("app", "sidecar"):
            text = (base / ("Caddyfile." + peer)).read_text()
            bad_client = (peer == "app" and variant == "invocation-client") or (
                peer == "sidecar" and variant == "callback-client"
            )
            bad_server = (peer == "sidecar" and variant == "invocation-server") or (
                peer == "app" and variant == "callback-server"
            )
            if bad_client:
                text = text.replace(peer + "-client", peer + "-wrong-ca-client")
            if bad_server:
                text = text.replace(peer + "-server", peer + "-wrong-ca-server")
                # Browser ingress remains independently valid for callback server negative.
                if peer == "app":
                    marker = text.index(":8444")
                    text = text[:marker] + text[marker:].replace(
                        "app-wrong-ca-server", "app-server"
                    )
            if (peer == "sidecar" and variant == "submission-loss") or (
                peer == "app" and variant == "callback-loss"
            ):
                text = text.replace(
                    "127.0.0.1:8080" if peer == "sidecar" else "127.0.0.1:8081",
                    "127.0.0.1:9081",
                    1,
                )
            (directory / ("Caddyfile." + peer)).write_text(text, encoding="utf-8")


def composition(directory, root, image, volume, recipe):
    material = directory / "material"
    tls = [f"{material.as_posix()}:/tls:ro"]
    # Individual TLS files prevent delivery of the independent signing subdirectory.
    tls = [f"{p.as_posix()}:/tls/{p.name}:ro" for p in material.glob("*.pem")]
    services = {}
    for peer, port in (("app", 8081), ("sidecar", 8080)):
        service = {
            "image": "eclipse-temurin:21-jre" if peer == "app" else image,
            "read_only": True,
            "tmpfs": ["/tmp:exec,mode=1777"],
            "environment": {
                (
                    "SPRING_CONFIG_LOCATION"
                    if peer == "app"
                    else "SPRING_CONFIG_ADDITIONAL_LOCATION"
                ): "file:/config/app.yaml"
                if peer == "app"
                else "file:/config/application.yaml"
            },
            "volumes": copy.copy(tls),
        }
        if peer == "app":
            service.update(
                user="10001:10001", command=["java", "-jar", "/app/reference.jar"]
            )
            service["volumes"] += [
                f"{(root / 'sdk/reference-app/target/sdk-reference-app-0.1.0-SNAPSHOT.jar').as_posix()}:/app/reference.jar:ro",
                f"{(directory / 'config/app.yaml').as_posix()}:/config/app.yaml:ro",
                f"{(material / 'signing').as_posix()}:/signing:ro",
                "public:/public",
            ]
        else:
            service["volumes"] += [
                f"{(directory / 'config/sidecar').as_posix()}:/config:ro",
                "public:/public:ro",
            ]
            service["tmpfs"] += ["/sidecar/data:uid=10001,gid=10001,mode=0700"]
            if recipe == "standard":
                # This harness gates on verified recipe-aware readiness itself.
                service["healthcheck"] = {"disable": True}
        owner = peer if recipe == "standard" else peer + "-proxy"
        if recipe == "standard":
            service["networks"] = ["remote"]
        else:
            service["network_mode"] = "service:" + owner
            services[owner] = {
                "image": "caddy:2.10.2",
                "read_only": True,
                "tmpfs": ["/config", "/data"],
                "networks": ["remote"],
                "volumes": copy.copy(tls)
                + [
                    f"{(directory / ('config/Caddyfile.' + peer)).as_posix()}:/etc/caddy/Caddyfile:ro"
                ],
            }
        services[peer] = service
        services[peer + "-fixture"] = {
            "image": "python:3.13-slim",
            "read_only": True,
            "network_mode": "service:" + owner,
            "environment": {"PYTHONDONTWRITEBYTECODE": "1", "SDK_LOCAL": "1"},
            "command": ["python", "/fixture.py"],
            "volumes": [
                f"{(root / 'scripts/sdk_lane/fixture.py').as_posix()}:/fixture.py:ro",
                f"{(root / 'scripts/sdk_lane/local_probe.py').as_posix()}:/local_probe.py:ro",
                f"{(root / 'scripts/sdk_lane/remote_probe.py').as_posix()}:/probe.py:ro",
                f"{(root / 'scripts/sdk_lane/remote_contract.py').as_posix()}:/remote_contract.py:ro",
                f"{(root / 'scripts/sdk_lane/remote_fault.py').as_posix()}:/fault.py:ro",
            ]
            + copy.copy(tls),
        }
    services["outsider"] = {
        "image": "python:3.13-slim",
        "read_only": True,
        "networks": ["remote"],
        "command": ["sleep", "infinity"],
        "volumes": copy.copy(tls)
        + [
            f"{(root / 'scripts/sdk_lane/remote_probe.py').as_posix()}:/probe.py:ro",
            f"{(root / 'scripts/sdk_lane/remote_contract.py').as_posix()}:/remote_contract.py:ro",
            f"{(root / 'scripts/sdk_lane/local_probe.py').as_posix()}:/local_probe.py:ro",
        ],
    }
    return {
        "services": services,
        "networks": {"remote": {"internal": True}},
        "volumes": {"public": {"external": True, "name": volume}},
    }


class Runtime:
    def __init__(
        self, directory, checkout, root, project, image, recipe, variant, call, failure
    ):
        self.call, self.failure = call, failure
        self.recipe, self.variant = recipe, variant
        self.project = project + "-" + variant
        self.volume = self.project + "-public"
        self.image = image
        directory.mkdir()
        remote_material.generate(directory / "material")
        self.signer_public = (
            x509.load_pem_x509_certificate(
                (directory / "material/signing/signer.pem").read_bytes()
            )
            .public_key()
            .public_numbers()
        )
        configure(directory / "config", checkout, recipe, variant)
        document = composition(directory, root, image, self.volume, recipe)
        dump(directory / "compose.yaml", document)
        self.compose = [
            "docker",
            "compose",
            "-p",
            self.project,
            "-f",
            str(directory / "compose.yaml"),
        ]

    def probe(self, name, service="app-fixture"):
        try:
            result = json.loads(
                self.call(
                    self.compose
                    + [
                        "exec",
                        "-T",
                        service,
                        "python",
                        "/probe.py",
                        self.recipe,
                        self.variant,
                        name,
                    ],
                    timeout=80,
                )
            )
        except Exception:
            raise self.failure("remote-" + name + "-failed") from None
        expected = observations(self.recipe, self.variant, name)
        if type(result) is not dict or json.dumps(result, sort_keys=True) != json.dumps(
            expected, sort_keys=True
        ):
            raise self.failure("remote-" + name + "-invalid-result")
        return result

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
                self.volume + ":/public",
                "--entrypoint",
                "sh",
                self.image,
                "-c",
                "chown 10001:10001 /public && chmod 0755 /public",
            ],
            timeout=30,
        )
        if self.recipe == "hardened":
            for peer in ("app", "sidecar"):
                self.call(
                    self.compose
                    + [
                        "run",
                        "--rm",
                        "--no-deps",
                        peer + "-proxy",
                        "caddy",
                        "validate",
                        "--config",
                        "/etc/caddy/Caddyfile",
                        "--adapter",
                        "caddyfile",
                    ],
                    timeout=60,
                )
            self.call(
                self.compose + ["up", "-d", "app-proxy", "sidecar-proxy"], timeout=90
            )
        self.call(
            self.compose + ["up", "-d", "app", "app-fixture", "outsider"], timeout=90
        )
        self.wait("app-ready")
        public = json.loads(
            self.call(self.compose + ["exec", "-T", "app", "cat", "/public/jwks.json"])
        )
        if set(public) != {"keys"} or len(public["keys"]) != 1:
            raise self.failure("remote-public-export-invalid")
        jwk = public["keys"][0]

        def number(value):
            return int.from_bytes(
                base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)), "big"
            )

        if (
            any(name in jwk for name in ("d", "p", "q", "dp", "dq", "qi"))
            or jwk.get("kty") != "RSA"
            or number(jwk["n"]) != self.signer_public.n
            or number(jwk["e"]) != self.signer_public.e
        ):
            raise self.failure("remote-public-export-invalid")
        self.call(self.compose + ["up", "-d", "sidecar", "sidecar-fixture"], timeout=90)
        self.wait("sidecar-ready")
        if self.variant.endswith("loss"):
            peer = "sidecar" if self.variant == "submission-loss" else "app"
            self.call(
                self.compose
                + [
                    "exec",
                    "-d",
                    peer + "-fixture",
                    "python",
                    "/fault.py",
                    self.recipe,
                    peer,
                ]
            )
            self.wait("fault-ready", peer + "-fixture")

    def wait(self, name, service="app-fixture"):
        deadline = time.monotonic() + 120
        while True:
            try:
                return self.probe(name, service)
            except self.failure:
                if name in ("app-ready", "sidecar-ready"):
                    peer = name.split("-")[0]
                    container = self.call(
                        self.compose + ["ps", "--all", "-q", peer]
                    ).strip()
                    if container:
                        state = json.loads(
                            self.call(
                                [
                                    "docker",
                                    "inspect",
                                    "--format",
                                    "{{json .State}}",
                                    container,
                                ]
                            )
                        )
                        if not state.get("Running"):
                            raise self.failure("remote-" + peer + "-exited") from None
                if time.monotonic() >= deadline:
                    raise self.failure("remote-" + name + "-timeout") from None
                time.sleep(0.3)

    def run(self):
        if self.variant == "isolation":
            self.probe("isolation", "outsider")
            self.probe("fixed-app")
            self.probe("fixed-sidecar", "sidecar-fixture")
            return {"passed": True}
        result = self.probe("scenario")
        if self.variant.endswith("loss"):
            self.probe(
                "loss-counts",
                "sidecar-fixture"
                if self.variant == "submission-loss"
                else "app-fixture",
            )
        return result

    def cleanup(self):
        try:
            try:
                helpers = self.call(
                    [
                        "docker",
                        "ps",
                        "-aq",
                        "--filter",
                        "label=loomspan.sdk.helper=" + self.project,
                    ]
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
