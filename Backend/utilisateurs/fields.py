from django.db import models
from .encryption import fernet

class EncryptedBinaryField(models.BinaryField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return fernet.decrypt(value)
        except Exception:
            return value

    def to_python(self, value):
        if value is None or isinstance(value, bytes):
            return value
        return fernet.decrypt(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return fernet.encrypt(value)
