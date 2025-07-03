from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager 
from django.core.validators import validate_email
from phonenumber_field.modelfields import PhoneNumberField
from cryptography.fernet import Fernet
from django.utils import timezone
from datetime import timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .fields import EncryptedBinaryField


# Create your models here.

# Cypher datamodel
#Fernet = Fernet.generate_key()

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
    email = models.EmailField(validators=[validate_email], unique=True)
    phone_number = PhoneNumberField(region='SN', blank=True, null=True, unique=True)
    two_factor_method = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='email'
    )
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now=True) 
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_birth']

    objects = CustomUserManager()
    
    class Meta: 
        abstract = False #pour permettre à BasicUser d'etre utiliser comme classe abstraite

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_account_locked(self):
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        self.save()

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 3: # Blocking after 3 attempts failed
            self.locked_until = timezone.now() + timedelta(minutes=15)
        
        self.save()


# Patients Class
class Patient(models.Model):
    user = models.OneToOneField(BasicUser, on_delete=models.CASCADE, related_name='patient_profile')
    #cni = models.CharField(max_length=13, unique=True)
    #assurances
    #assurance_name models.CharField(
    #    max_length=30,
    #    choices=[('allianz', 'ALLIANZ')]
    #)
    #assurance_card_id = models.CharField()
    weight = models.IntegerField()
    blood_type = models.CharField(max_length=4)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Patient)"


# Doctors Class
class Doctor(models.Model):
    user = models.OneToOneField(BasicUser, on_delete=models.CASCADE, related_name='doctor_profile')
    licence_number = models.CharField(max_length=30, unique=True)
    specialisation = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    private_key = EncryptedBinaryField(null=True, blank=True) #Encrypting the private keys so we can't store it on plain text form
    public_key = models.TextField(null=True, blank=True)

    def generate_key_pair(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        self.save()

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


# Pharmacist Class
class Pharmacist(models.Model):
    user = models.OneToOneField(BasicUser, on_delete=models.CASCADE, related_name='pharmacist_profile')
    licence_number = models.CharField(max_length=30, unique=True)
    pharmacy_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.user.get_full_name()} (Pharmacien)"


# Login Attempt Class
class LoginAttempt(models.Model):
    user = models.ForeignKey(BasicUser, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Tentative de connexion'
        verbose_name_plural = 'Tentatives de connexion'

    def __str__(self):
        return f"{self.user.email} - {'Success' if self.success else 'Failed'} - {self.timestamp}"