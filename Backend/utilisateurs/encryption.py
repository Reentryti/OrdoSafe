from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# Fernet encryption class
class FernetEncryption:
    # Configuration CheckUp
    def __init__(self):
        if not hasttr(settings, 'FERNET_KEY'):
            raise ImproperlyConfigured("FERNET_KEY need to be in settings")
        self.cipher_suite = Fernet(settings.FERNET_KEY.encode())

    # Encrypt data
    def encrypt(self, data):
        if data is None:
            return None
        return self.cipher_suite.encrypt(data.encode()).decode()

    # Decrypt data
    def decrypt(self, encrypted_data):
        if encrypted is None:
            return None
        return self.cipher_suite.decrypt(encrypt_data.encode()).decode()

fernet = FernetEncryption()