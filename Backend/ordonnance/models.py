from django.db import models
from django.contrib.auth.models import User

class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    frequence = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nom} - {self.dosage}"

class Ordonnance(models.Model):
    patient = models.ForeignKey(User, related_name='ordonnances_patient', on_delete=models.CASCADE)
    medecin = models.ForeignKey(User, related_name='ordonnances_medecin', on_delete=models.CASCADE)
    medicaments = models.ManyToManyField(Medicament)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, default='brouillon')
    signature = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ordonnance #{self.id} - {self.patient.username}"
