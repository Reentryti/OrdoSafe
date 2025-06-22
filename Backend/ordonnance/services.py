from OpenSSL import crypto
from cryptography.fernet import Fernet
from django.conf import settings
import hashlib
import json
import os
#from audit.utils import log_security_event


# Cryptography class function
class CryptoService:
    @staticmethod
    # Encryption function
    def encrypt_data(data: dict) -> bytes:
        fernet = Fernet(settings.FERNET_KEY.encode())
        return fernet.encrypt(json.dumps(data).encode())

    # Decryption function
    @staticmethod
    def decrypt_data(encrypted_data: bytes) -> dict:
        fernet = Fernet(settings.FERNET_KEY.encode())
        return json.loads(fernet.decrypt(encrypted_data).decode())



# Signature class
class SignatureService:
    # Generating RSA key function
    @staticmethod
    def generate_key_pair(doctor_id: int, key_dir='keys'):
        # Key management
        os.makedirs(key_dir, exist_ok=True)
        
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        
        cert = crypto.X509()
        cert.get_subject().CN = f"Doctor {doctor_id}"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)  # Validité 10 ans
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        private_key_path = os.path.join(key_dir, f"doctor_{doctor_id}_private.pem")
        certificate_path = os.path.join(key_dir, f"doctor_{doctor_id}_cert.pem")
        
        with open(private_key_path, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        
        with open(certificate_path, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        
        return private_key_path, certificate_path

    # Data signature function (using private key)
    @staticmethod
    def sign_data(data: str, private_key_path: str) -> str:
        
        with open(private_key_path, "rb") as f:
            private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
        
        signature = crypto.sign(private_key, data.encode(), 'sha256')
        return signature.hex()

    # Signature verification function
    @staticmethod
    def verify_signature(data: str, signature: str, certificate: str) -> bool:
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate.encode())
            crypto.verify(cert, bytes.fromhex(signature), data.encode(), 'sha256')
            return True
        except Exception as e:
            #log_security_event(
             #   action='signature_verification_failed',
              #  metadata={'error': str(e)}
            #)
            return False


# Ordonnance encryption and signature function defines
class OrdonnanceSecurityService:
    # Ordonnance Signature
    @staticmethod
    def prepare_for_signing(ordonnance) -> str:
        return f"{ordonnance.id}{ordonnance.patient.id}{ordonnance.medecin.id}{ordonnance.date_creation}"

    @classmethod
    def sign_ordonnance(cls, ordonnance, doctor):
        # Hashing data
        data_hash = hashlib.sha256(cls.prepare_for_signing(ordonnance).encode()).hexdigest()
        
        # Keys path
        private_key_path = f"keys/doctor_{doctor.id}_private.pem"
        certificate_path = f"keys/doctor_{doctor.id}_cert.pem"
        if not (os.path.exists(private_key_path) and os.path.exists(certificate_path)):
            private_key_path, certificate_path = SignatureService.generate_key_pair(doctor.id)
        
        # Signature
        signature = SignatureService.sign_data(data_hash, private_key_path)
        
        # Certificate
        with open(certificate_path, "rb") as f:
            certificate = f.read().decode()
        
        return signature, certificate