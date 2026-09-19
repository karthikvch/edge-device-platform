from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def generate_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def save_private_key(
    private_key: rsa.RSAPrivateKey,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    path.write_bytes(private_bytes)

    # Owner read/write only.
    path.chmod(0o600)


def generate_csr(
    private_key: rsa.RSAPrivateKey,
    device_id: str,
) -> bytes:
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(
                        NameOID.COMMON_NAME,
                        device_id,
                    )
                ]
            )
        )
        .sign(
            private_key,
            hashes.SHA256(),
        )
    )

    return csr.public_bytes(
        serialization.Encoding.PEM
    )