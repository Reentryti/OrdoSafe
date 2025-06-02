from django.db import models

# Create your models here.


# Basic Users Class
class BasicUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_birth = models.DateField()
    

    class Meta: 
        abstract = True

# Patients Class
class Patient(BasicUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    weight = models.IntegerField()
    blood_type = models.CharField(max_length=4)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Patient)"

# Doctors Class
class Doctor(BasicUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    licence_number = models.CharField(max_length=30)
    specialisation = models.CharField(max_length=30)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


# Pharmacist Class
class Pharmacist(BasicUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacist')
    licence_number = models.CharField(max_length=30)
    pharmacy_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.get_full_name()} (Pharmacien)"