"""Offline, disposable TLS peers and independent provided RSA signer."""

from datetime import datetime, timedelta, timezone
import base64
import hashlib
import json

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def generate(directory):
    directory.mkdir()
    now = datetime.now(timezone.utc)

    def key():
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def save(label, private, certificate):
        (directory / (label + ".pem")).write_bytes(
            certificate.public_bytes(serialization.Encoding.PEM)
        )
        (directory / (label + "-key.pem")).write_bytes(
            private.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    authorities = {}
    for label in ("group", "other"):
        private = key()
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, label)])
        certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(private.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=2))
            .not_valid_after(now + timedelta(days=2))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private.public_key()),
                critical=False,
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(
                    private.public_key()
                ),
                critical=False,
            )
            .add_extension(
                x509.KeyUsage(True, False, False, False, False, True, True, None, None),
                critical=True,
            )
            .sign(private, hashes.SHA256())
        )
        authorities[label] = private, certificate
        (directory / (label + "-ca.pem")).write_bytes(
            certificate.public_bytes(serialization.Encoding.PEM)
        )
    (directory / "jvm-truststore.p12").write_bytes(
        pkcs12.serialize_java_truststore(
            [pkcs12.PKCS12Certificate(authorities["group"][1], b"fixture-group")],
            serialization.BestAvailableEncryption(b"fixture-public-trust"),
        )
    )
    for peer in ("app", "sidecar"):
        for kind in (
            "server",
            "client",
            "wrong-ca-server",
            "wrong-ca-client",
            "wrong-host",
            "expired",
        ):
            private = key()
            ca_key, ca = authorities[
                "other" if kind.startswith("wrong-ca") else "group"
            ]
            host = "wrong.invalid" if kind == "wrong-host" else peer
            certificate = (
                x509.CertificateBuilder()
                .subject_name(
                    x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, peer)])
                )
                .issuer_name(ca.subject)
                .public_key(private.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(now - timedelta(days=2))
                .not_valid_after(now + timedelta(days=-1 if kind == "expired" else 1))
                .add_extension(
                    x509.BasicConstraints(ca=False, path_length=None), critical=True
                )
                .add_extension(
                    x509.AuthorityKeyIdentifier.from_issuer_public_key(
                        ca_key.public_key()
                    ),
                    critical=False,
                )
                .add_extension(
                    x509.SubjectKeyIdentifier.from_public_key(private.public_key()),
                    critical=False,
                )
                .add_extension(
                    x509.SubjectAlternativeName(
                        [x509.DNSName(host), x509.DNSName(host + "-proxy")]
                    ),
                    critical=False,
                )
                .add_extension(
                    x509.ExtendedKeyUsage(
                        [
                            ExtendedKeyUsageOID.CLIENT_AUTH
                            if "client" in kind
                            else ExtendedKeyUsageOID.SERVER_AUTH
                        ]
                    ),
                    critical=False,
                )
                .sign(ca_key, hashes.SHA256())
            )
            save(peer + "-" + kind, private, certificate)
    for label in ("signing", "replacement"):
        signing_material(directory / label, key(), now)


def signing_material(signing, private, now):
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "provided signer")])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(private, hashes.SHA256())
    )
    signing.mkdir()
    (signing / "signer.pem").write_bytes(
        certificate.public_bytes(serialization.Encoding.PEM)
    )
    (signing / "signer-key.pem").write_bytes(
        private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )


def public_jwk(certificate):
    numbers = (
        x509.load_pem_x509_certificate(certificate.read_bytes())
        .public_key()
        .public_numbers()
    )

    def encoded(n):
        return (
            base64.urlsafe_b64encode(n.to_bytes((n.bit_length() + 7) // 8, "big"))
            .rstrip(b"=")
            .decode()
        )

    fields = {"e": encoded(numbers.e), "kty": "RSA", "n": encoded(numbers.n)}
    thumbprint = hashlib.sha256(
        json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
    ).digest()
    return fields | {
        "kid": base64.urlsafe_b64encode(thumbprint).rstrip(b"=").decode(),
        "use": "sig",
        "alg": "RS256",
    }
