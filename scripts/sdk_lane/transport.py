"""Per-run transport material and checks in the SDK lane's existing Compose runtime."""

from datetime import datetime, timedelta, timezone
import time

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import yaml


def certificates(directory):
    now = datetime.now(timezone.utc)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "SDK fixture CA")])
    ca = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=2))
        .not_valid_after(now + timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=None,
                decipher_only=None,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    (directory / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    for label, expired in (("valid", False), ("expired", True)):
        leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        leaf = (
            x509.CertificateBuilder()
            .subject_name(
                x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "sidecar")])
            )
            .issuer_name(name)
            .public_key(leaf_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=2))
            .not_valid_after(now + timedelta(days=-1 if expired else 1))
            .add_extension(
                x509.SubjectAlternativeName(
                    [x509.DNSName(n) for n in ("localhost", "sidecar", "fixtures")]
                ),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )
        (directory / f"{label}.pem").write_bytes(
            leaf.public_bytes(serialization.Encoding.PEM)
        )
        (directory / f"{label}-key.pem").write_bytes(
            leaf_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )


# Executed in the fixture container. Only fixed booleans/status leave the process.
TLS_PROBE = """
import http.client,json,socket,ssl
host,port,mode=ARGS
context=ssl.create_default_context(cafile='/tls/ca.pem') if mode != 'wrong-ca' else ssl.create_default_context()
if mode == 'ready':
    context.check_hostname=False
    context.verify_mode=ssl.CERT_NONE
try:
    with socket.create_connection((host,port),timeout=3) as raw:
        with context.wrap_socket(raw,server_hostname='wrong.invalid' if mode == 'wrong-host' else ('sidecar' if host == 'expired' else host)) as stream:
            stream.sendall(b'GET /actuator/health/readiness HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n')
            response=http.client.HTTPResponse(stream); response.begin()
            body=json.loads(response.read())
            assert response.status == 200 and body == {'status':'UP'}
    assert mode in ('trusted','ready')
    print(json.dumps({'trusted':True}))
except ssl.SSLCertVerificationError as error:
    assert mode in ('wrong-ca','wrong-host','expired')
    if mode == 'wrong-host': assert error.verify_code == 62
    if mode == 'expired': assert error.verify_code == 10
    print(json.dumps({'rejected':True}))
"""


def probe(runtime, host, port, mode):
    return runtime.python(
        "fixtures", "ARGS=" + repr((host, port, mode)) + "\n" + TLS_PROBE
    )


def wait_probe(runtime, host, port, mode):
    deadline = time.monotonic() + 120
    while True:
        try:
            return probe(runtime, host, port, mode)
        except runtime.failure:
            if time.monotonic() >= deadline:
                raise runtime.failure("transport-readiness-timeout") from None
            time.sleep(1)


def run(runtime):
    """Independent direct-TLS servers and supplied Caddy; no live replacement/reload."""
    tls = runtime.directory / "tls"
    tls.mkdir()
    certificates(tls)
    config = runtime.directory / "config"
    original = yaml.safe_load((config / "application.yaml").read_bytes())
    services = {}
    for service, label in (("sidecar", "valid"), ("expired", "expired")):
        settings = dict(original)
        settings["server"] = {
            "ssl": {
                "enabled": True,
                "certificate": f"file:/tls/{label}.pem",
                "certificate-private-key": f"file:/tls/{label}-key.pem",
            },
            "shutdown": "graceful",
        }
        (config / f"{label}.yaml").write_text(
            yaml.safe_dump(settings), encoding="utf-8"
        )
        base = {
            "image": runtime.image,
            "environment": {
                "SPRING_CONFIG_ADDITIONAL_LOCATION": f"file:/config/{label}.yaml"
            },
            "volumes": [f"{config.as_posix()}:/config:ro", f"{tls.as_posix()}:/tls:ro"],
            "networks": ["sdk"],
            "tmpfs": [
                "/sidecar/data:uid=10001,gid=10001,mode=0700",
                "/tmp:exec,mode=1777",
            ],
            "read_only": True,
        }
        services[service] = base
    services["fixtures"] = {
        "environment": {"SDK_FIXTURE_BIND": "127.0.0.1"},
        "volumes": [f"{tls.as_posix()}:/tls:ro"],
    }
    supplied = runtime.checkout / "examples/production/Caddyfile.supplied"
    # A per-run copy gives the shipped config its expected filenames, once before startup.
    (tls / "fullchain.pem").write_bytes((tls / "valid.pem").read_bytes())
    (tls / "privkey.pem").write_bytes((tls / "valid-key.pem").read_bytes())
    services["caddy"] = {
        "image": "caddy:2.10.2",
        "network_mode": "service:fixtures",
        "environment": {"SITE_HOST": "localhost", "HTTPS_PORT": "8443"},
        "volumes": [
            f"{supplied.as_posix()}:/etc/caddy/Caddyfile:ro",
            f"{tls.as_posix()}:/etc/caddy/certs:ro",
        ],
        "depends_on": ["fixtures"],
    }
    override = runtime.directory / "transport.yaml"
    override.write_text(yaml.safe_dump({"services": services}), encoding="utf-8")
    runtime.extra_compose = runtime.compose + ["-f", str(override)]
    runtime.call(
        runtime.extra_compose
        + ["up", "-d", "--force-recreate", "sidecar", "expired", "fixtures", "caddy"],
        timeout=180,
    )
    wait_probe(runtime, "sidecar", 8080, "trusted")
    before = runtime.counts()
    outcomes = {
        mode: probe(runtime, "sidecar", 8080, mode)
        for mode in ("wrong-ca", "wrong-host")
    }
    wait_probe(runtime, "expired", 8080, "ready")
    outcomes["expired"] = probe(runtime, "expired", 8080, "expired")
    # Caddy's fixed upstream is the existing fixture in its namespace, never the supplied hostile host.
    script = """
import http.client,json,socket,ssl
context=ssl.create_default_context(cafile='/tls/ca.pem')
with socket.create_connection(('fixtures',8443),timeout=3) as raw:
    with context.wrap_socket(raw,server_hostname='localhost') as stream:
        stream.sendall(b'GET /headers HTTP/1.1\\r\\nHost: localhost:1\\r\\nForwarded: host=evil.invalid;proto=http\\r\\nX-Forwarded-Host: localhost:1\\r\\nX-Forwarded-Proto: http\\r\\nX-Forwarded-Port: 1\\r\\nX-Forwarded-Prefix: /evil\\r\\nConnection: close\\r\\n\\r\\n')
        response=http.client.HTTPResponse(stream);response.begin()
        assert response.status == 200
        headers={key.lower():value for key,value in json.loads(response.read()).items()}
        assert headers['host'] == 'localhost:8443'
        assert headers['x-forwarded-host'] == 'localhost:8443' and headers['x-forwarded-proto'] == 'https'
        assert not {'forwarded','x-forwarded-port','x-forwarded-prefix'} & headers.keys()
        assert 'evil.invalid' not in json.dumps(headers)
connection=http.client.HTTPConnection('fixtures',80,timeout=3)
connection.request('GET','/management/login',headers={'Host':'localhost:1','X-Forwarded-Host':'evil.invalid'})
response=connection.getresponse()
assert response.status in (301,302,307,308)
assert response.getheader('Location') == 'https://localhost:8443/management/login'
connection.close()
try:
    with socket.create_connection(('fixtures',8080),timeout=3): pass
    raise AssertionError('backend bypass')
except ConnectionRefusedError: pass
try:
    with socket.create_connection(('fixtures',8443),timeout=3) as raw:
        with ssl.create_default_context().wrap_socket(raw,server_hostname='localhost'): pass
    raise AssertionError('wrong trust accepted')
except ssl.SSLCertVerificationError: pass
print(json.dumps({'normalized':True,'fixedUpstream':True,'redirect':True,'wrongTrustRejected':True}))
"""
    # Wait for Caddy with this positive request, never interpret refusal as TLS rejection.
    deadline = time.monotonic() + 60
    while True:
        try:
            outcomes["caddy"] = runtime.python("sidecar", script, service_python=False)
            break
        except runtime.failure:
            if time.monotonic() >= deadline:
                raise runtime.failure("caddy-transport-timeout") from None
            time.sleep(1)
    if runtime.counts() != before:
        raise runtime.failure("transport-rejection-side-effect")
    return outcomes
