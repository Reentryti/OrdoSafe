from django.db import models
from django.contrib.auth import get_user_model
from utilisateurs.models import Patient, Doctor
from django.conf import settings
from cryptography.fernet import Fernet
import json


User = get_user_model()

class Ordonnance(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('issued', 'Émise'),
        ('cancelled', 'Annulée'),
        ('fulfilled', 'Honorée'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='ordonnance_patient')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='ordonnance_doctor')
    medicaments = models.JSONField() 
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    signature = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ordonnance_created')
    _encrypted_data = models.BinaryField(null=True, blank=True)

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
        self.sensitive_data = {
            'patient_info': {
                'id': self.patient.id,
                'nom': self.patient.user.get_full_name()
            },
            'doctor_info': {
                'id': self.doctor.id,
                'nom': self.doctor.user.get_full_name()
            },
            'medicaments': self.medicaments  # Chiffrer aussi si nécessaire
        }
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Ordonnance #{self.id} - {self.patient}"