from django.db import models
from django.contrib.auth import get_user_model
from utilisateurs.models import Doctor
from django.conf import settings
from cryptography.fernet import Fernet
import json
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string

User = get_user_model()

class Ordonnance(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('issued', 'Émise'),
        ('cancelled', 'Annulée'),
        ('fulfilled', 'Honorée'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='ordonnances')
    date_creation = models.DateTimeField(auto_now_add=True)
    medicaments = models.JSONField()
    patient_last_name = models.CharField(blank=True, null=True, max_length=255)
    patient_first_name = models.CharField(blank=True, null=True, max_length=255)
    patient_date_birth = models.DateField(blank=True, null=True)
    patient_phone = PhoneNumberField(region='SN', blank=True, null=True, unique=True, db_index=True)
    patient_email = models.EmailField(blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    signature = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ordonnances_created')
    _encrypted_data = models.BinaryField(null=True, blank=True)

    #Kind of brute force response
    access_code = models.CharField(max_length=10, unique=True, editable=False, blank=True)


    def sign(self, doctor):
        if not doctor.private_key:
            raise ValueError("Le médecin n'a pas de clé privée configurée.")

        data_to_sign = json.dumps({
            'patient_last_name': self.patient_last_name,
            'patient_first_name': self.patient_first_name,
            'patient_date_birth': str(self.patient_date_birth),
            'patient_telephone': str(self.patient_phone),
            'patient_email': self.patient_email,
            'doctor_id': self.doctor.id,
            'medicaments': self.medicaments,
            'date_creation': str(self.date_creation)
        }).encode('utf-8')

        private_key = serialization.load_pem_private_key(
            doctor.private_key.encode() if isinstance(doctor.private_key, str) else doctor.private_key,
            password=None
        )

        signature = private_key.sign(
            data_to_sign,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        self.signature = base64.b64encode(signature).decode('utf-8')
        self.status = 'issued'
        self.save()

    def verify_signature(self):
        if not self.signature or not self.doctor.public_key:
            return False

        public_key = serialization.load_pem_public_key(self.doctor.public_key.encode('utf-8'))

        data = json.dumps({
            'patient_last_name': self.patient_last_name,
            'patient_first_name': self.patient_first_name,
            'patient_date_birth': str(self.patient_date_birth),
            'doctor_id': self.doctor.id,
            'medicaments': self.medicaments,
            'date_creation': str(self.date_creation)
        }).encode('utf-8')

        try:
            public_key.verify(
                base64.b64decode(self.signature.encode('utf-8')),
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    @property
    def sensitive_data(self):
        if not self._encrypted_data:
            return {}
        fernet = Fernet(settings.FERNET_KEY.encode())
        return json.loads(fernet.decrypt(self._encrypted_data).decode())

    @sensitive_data.setter
    def sensitive_data(self, value):
        fernet = Fernet(settings.FERNET_KEY.encode())
        self._encrypted_data = fernet.encrypt(json.dumps(value).encode())

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = get_random_string(8).upper()

        self.sensitive_data = {
            'patient_info': {
                'last_name': self.patient_last_name,
                'first_name': self.patient_first_name,
                'date_birth': str(self.patient_date_birth),
                'phone': str(self.patient_phone),
                'email': self.patient_email,
            },
            'doctor_info': {
                'id': self.doctor.id,
                'nom': self.doctor.user.get_full_name()
            },
            'medicaments': self.medicaments
        }
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ordonnance #{self.id} - {self.patient_last_name} {self.patient_first_name}"
