"""Bounded recipe adaptations for the non-web fixture; no new production contracts."""

import json
import time
import yaml
from sdk_lane.outbound_probe import RESULT


def configure(config):
    app_path = config / "application.yaml"
    app = yaml.safe_load(app_path.read_text())
    app["loomspan"]["skills"]["locations"] = ["file:/config/localModel.yaml"]
    app["loomspan"]["connections"] = {
        "normal": app["loomspan"]["connections"]["normal"]
    }
    app["loomspan"]["models"] = {"normal": app["loomspan"]["models"]["normal"]}
    app_path.write_text(yaml.safe_dump(app), encoding="utf-8")
    (config / "routes.yaml").write_text(
        yaml.safe_dump({"targets": {}, "routes": {}}), encoding="utf-8"
    )
    for path in config.glob("local*.yaml"):
        if path.name != "localModel.yaml":
            path.unlink()


def adapt(document, root, host):
    document["services"][host]["command"] += [
        "--spring.main.web-application-type=none",
        "--fixture.outbound-only=true",
    ]
    for name, service in document["services"].items():
        if name in ("fixtures", "app-fixture", "sidecar-fixture", "outsider"):
            service["volumes"].append(
                f"{(root / 'scripts/sdk_lane/outbound_probe.py').as_posix()}:/outbound_probe.py:ro"
            )


def probe(runtime, recipe, action, service):
    try:
        value = json.loads(
            runtime.call(
                runtime.compose
                + [
                    "exec",
                    "-T",
                    service,
                    "python",
                    "/outbound_probe.py",
                    recipe,
                    action,
                ],
                timeout=35,
            )
        )
    except Exception:
        raise runtime.failure("outbound-" + action + "-failed") from None
    expected = RESULT if action == "scenario" else {"passed": True}
    if json.dumps(value, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise runtime.failure("outbound-" + action + "-invalid-result")
    return value


def ready(runtime, recipe, service):
    deadline = time.monotonic() + 120
    while True:
        try:
            probe(runtime, recipe, "ready", service)
            return
        except runtime.failure:
            if time.monotonic() >= deadline:
                raise runtime.failure("outbound-startup-timeout") from None
            time.sleep(0.3)


def run(runtime, recipe):
    host = "host" if recipe == "local" else "app"
    service = "fixtures" if recipe == "local" else "app-fixture"

    def state():
        container = runtime.call(runtime.compose + ["ps", "--all", "-q", host]).strip()
        return json.loads(
            runtime.call(
                ["docker", "inspect", "--format", "{{json .State}}", container]
            )
        )

    if not state().get("Running"):
        raise runtime.failure("outbound-process-not-alive")
    if recipe == "hardened":
        probe(runtime, recipe, "outsider", "outsider")
        probe(runtime, recipe, "egress", "sidecar-fixture")
    result = probe(runtime, recipe, "scenario", service)
    if recipe != "local":
        probe(runtime, recipe, "models", "sidecar-fixture")
    deadline = time.monotonic() + 10
    while state().get("Running"):
        if time.monotonic() >= deadline:
            raise runtime.failure("outbound-exit-timeout")
        time.sleep(0.1)
    final = state()
    if final.get("ExitCode") != 0 or final.get("OOMKilled") or final.get("Error"):
        raise runtime.failure("outbound-process-failed")
    return result
