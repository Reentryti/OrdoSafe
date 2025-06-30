from django.db import models
from django.contrib.auth import get_user_model
from utilisateurs.models import Patient, Doctor
from django.conf import settings
from cryptography.fernet import Fernet
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from cryptography.hazmat.primitives import serialization



User = get_user_model()

class Ordonnance(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('issued', 'Émise'),
        ('cancelled', 'Annulée'),
        ('fulfilled', 'Honorée'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='ordonnance_as_patient')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='ordonnance_as_doctor')
    medicaments = models.JSONField() 
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    signature = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ordonnance_created')
    _encrypted_data = models.BinaryField(null=True, blank=True)

    def sign(self, doctor):
        if not doctor.private_key:
            raise ValueError("Le médecin n'a pas de clé privée configurée.")
        
        #Get data to sign
        data_to_sign = json.dumps({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'medicaments': self.medicaments,
            'date_creation': str(self.date_creation)
        }).encode('utf-8')

        # Load the private key
        private_key = serialization.load_pem_private_key(
            doctor.private_key,
            password=None
        )

        #Signature
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

        # Load public key
        public_key = serialization.load_pem_public_key(
            self.doctor.public_key.encode('utf-8')
        )

        
        data = json.dumps({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'medicaments': self.medicaments,
            'date_creation': str(self.date_creation)
        }).encode('utf-8')

        # Verify integrity
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
        if self._state.adding or self.has_changed(): 
            self.sensitive_data = {
                'patient_info': {
                    'id': self.patient.id,
                    'nom': self.patient.user.get_full_name()
                },
                'doctor_info': {
                    'id': self.doctor.id,
                    'nom': self.doctor.user.get_full_name()
                },
                'medicaments': self.medicaments  # Chiffrement en would
            }
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Ordonnance #{self.id} - {self.patient}"