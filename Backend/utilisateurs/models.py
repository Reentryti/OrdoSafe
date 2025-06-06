from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager 

# Create your models here.

# Customize User Creation
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extrafields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extrafields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extrafields):
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extrafields)

# Basic Users Class
class BasicUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_birth = models.DateField()
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_birth']

    objects = CustomUserManager()
    
    class Meta: 
        abstract = False #pour permettre à BasicUser d'etre utiliser comme classe abstraite

# Patients Class
class Patient(BasicUser):
    user = models.OneToOneField(BasicUser, on_delete=models.CASCADE, related_name='patient_profile')
    #cni = models.CharField(max_length=13, unique=True)
    weight = models.IntegerField()
    blood_type = models.CharField(max_length=4)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Patient)"

# Doctors Class
class Doctor(BasicUser):
    user = models.OneToOneField(BasicUser, on_delete=models.CASCADE, related_name='doctor_profile')
    licence_number = models.CharField(max_length=30, unique=True)
    specialisation = models.CharField(max_length=30)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


# Pharmacist Class
class Pharmacist(BasicUser):
    user = models.OneToOneField(BasicUser, on_delete=models.CASCADE, related_name='pharmacist_profile')
    licence_number = models.CharField(max_length=30, unique=True)
    pharmacy_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.get_full_name()} (Pharmacien)"