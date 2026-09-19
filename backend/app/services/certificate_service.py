import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


CA_CERT_PATH = Path(
    os.getenv("EDP_CA_CERT", "/app/certs/ca/ca.crt")
)

CA_KEY_PATH = Path(
    os.getenv("EDP_CA_KEY", "/app/certs/ca/ca.key")
)

CERT_VALIDITY_DAYS = 365


def load_ca_certificate():
    ca_cert_data = CA_CERT_PATH.read_bytes()

    return x509.load_pem_x509_certificate(ca_cert_data)


def load_ca_private_key():
    ca_key_data = CA_KEY_PATH.read_bytes()

    return serialization.load_pem_private_key(
        ca_key_data,
        password=None,
    )


def validate_csr(
    csr: x509.CertificateSigningRequest,
    device_id: str,
):
    if not csr.is_signature_valid:
        raise ValueError("CSR signature is invalid")

    common_names = csr.subject.get_attributes_for_oid(
        NameOID.COMMON_NAME
    )

    if not common_names:
        raise ValueError("CSR does not contain a Common Name")

    common_name = common_names[0].value

    if common_name != device_id:
        raise ValueError(
            "CSR Common Name does not match device_id"
        )


def issue_device_certificate(
    device_id: str,
    csr_pem: str,
):
    csr = x509.load_pem_x509_csr(
        csr_pem.encode("utf-8")
    )

    validate_csr(csr, device_id)

    ca_certificate = load_ca_certificate()
    ca_private_key = load_ca_private_key()

    now = datetime.now(timezone.utc)

    certificate = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_certificate.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(
            now + timedelta(days=CERT_VALIDITY_DAYS)
        )
        .add_extension(
            x509.BasicConstraints(
                ca=False,
                path_length=None,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage(
                [
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
                ]
            ),
            critical=False,
        )
        .sign(
            private_key=ca_private_key,
            algorithm=hashes.SHA256(),
        )
    )

    certificate_pem = certificate.public_bytes(
        serialization.Encoding.PEM
    ).decode("utf-8")

    ca_certificate_pem = ca_certificate.public_bytes(
        serialization.Encoding.PEM
    ).decode("utf-8")

    return {
        "certificate": certificate_pem,
        "ca_certificate": ca_certificate_pem,
        "serial": str(certificate.serial_number),
        "issued_at": certificate.not_valid_before_utc,
        "expires_at": certificate.not_valid_after_utc,
    }