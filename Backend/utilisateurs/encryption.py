from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# Fernet encryption class
class FernetEncryption:
    # Configuration CheckUp
    def __init__(self):
        if not hasattr(settings, 'FERNET_KEY'):
            raise ImproperlyConfigured("FERNET_KEY need to be in settings")
        self.cipher_suite = Fernet(settings.FERNET_KEY.encode())

    # Encrypt data
    def encrypt(self, data):
        if data is None:
            return None
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = str(data).encode('utf-8')

        encrypted_bytes = self.cipher_suite.encrypt(data_bytes)
        return encrypted_bytes.encode('utf-8')

    # Decrypt data
    def decrypt(self, encrypted_data):
        if encrypted_data is None:
            return None
        
        if isinstance(encrypted_data, str):
            encrypted_bytes = encrypted_data.encode('utf-8')
        elif isinstance(encrypted_data, bytes):
            encrypted_bytes = encrypted_data
        else:
            encrypted_bytes = str(encrypted_data).encode('utf-8')
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_bytes

fernet = FernetEncryption()