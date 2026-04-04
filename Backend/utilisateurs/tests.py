from django.test import TestCase

# Create your tests here.

import base64
from io import BytesIO
from datetime import date, timedelta
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice
from qrcode import QRCode
from .models import BasicUser, Patient, Doctor, Pharmacist, LoginAttempt
from .views import (
    setup_2fa,
    backup_codes,
    PatientLoginView,
    DoctorLoginView,
    PharmacistLoginView,
    patient_dash,
    doctor_dash,
    pharmacist_dash
)

User = get_user_model()

class BasicUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            date_birth=date(1990, 1, 1)
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpass123"))
        self.assertEqual(self.user.get_full_name(), "John Doe")
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_account_lock_functionality(self):
        # Test login attempts and account locking
        self.assertEqual(self.user.login_attempts, 0)
        self.assertFalse(self.user.is_account_locked())

        # Increment attempts
        self.user.increment_login_attempts()
        self.assertEqual(self.user.login_attempts, 1)
        self.assertFalse(self.user.is_account_locked())

        # Lock account after 3 attempts
        self.user.increment_login_attempts()
        self.user.increment_login_attempts()
        self.assertTrue(self.user.is_account_locked())

        # Test reset
        self.user.reset_login_attempts()
        self.assertEqual(self.user.login_attempts, 0)
        self.assertFalse(self.user.is_account_locked())

class ProfileModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            date_birth=date(1990, 1, 1))
        
    def test_patient_creation(self):
        patient = Patient.objects.create(
            user=self.user,
            weight=70,
            blood_type="A+",
            allergies="Peanuts"
        )
        self.assertEqual(str(patient), "John Doe (Patient)")
        self.assertEqual(patient.user.email, "test@example.com")

    def test_doctor_creation(self):
        doctor = Doctor.objects.create(
            user=self.user,
            licence_number="MD12345",
            specialisation="Cardiology"
        )
        self.assertEqual(str(doctor), "Dr. John Doe")

    def test_pharmacist_creation(self):
        pharmacist = Pharmacist.objects.create(
            user=self.user,
            licence_number="PH12345",
            pharmacy_name="City Pharmacy"
        )
        self.assertEqual(str(pharmacist), "John Doe (Pharmacien)")

class LoginAttemptModelTest(TestCase):
    def test_login_attempt_creation(self):
        attempt = LoginAttempt.objects.create(
            username="test@example.com",
            ip_address="127.0.0.1",
            success=True
        )
        self.assertEqual(str(attempt), "test@example.com - Success")

class TwoFactorAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            date_birth=date(1990, 1, 1))
        self.factory = RequestFactory()

    def test_setup_2fa_view(self):
        request = self.factory.get('/setup-2fa/')
        request.user = self.user
        
        # Setup message storage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = setup_2fa(request)
        self.assertEqual(response.status_code, 200)
        
        # Check if device was created
        device = TOTPDevice.objects.filter(user=self.user).first()
        self.assertIsNotNone(device)

    def test_backup_codes_view(self):
        # Setup 2FA first
        device = TOTPDevice.objects.create(user=self.user, name='default', confirmed=True)
        self.user.backup_codes = ['123456', '654321']
        self.user.save()

        request = self.factory.get('/backup-codes/')
        request.user = self.user
        request.session = {}
        
        response = backup_codes(request)
        self.assertEqual(response.status_code, 200)

class AuthViewsTest(TestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(
            email="patient@example.com",
            password="testpass123",
            first_name="Patient",
            last_name="User",
            date_birth=date(1990, 1, 1))
        self.patient = Patient.objects.create(
            user=self.patient_user,
            weight=70,
            blood_type="A+")

        self.doctor_user = User.objects.create_user(
            email="doctor@example.com",
            password="testpass123",
            first_name="Doctor",
            last_name="User",
            date_birth=date(1990, 1, 1))
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            licence_number="MD12345",
            specialisation="Cardiology")

        self.pharmacist_user = User.objects.create_user(
            email="pharmacist@example.com",
            password="testpass123",
            first_name="Pharmacist",
            last_name="User",
            date_birth=date(1990, 1, 1))
        self.pharmacist = Pharmacist.objects.create(
            user=self.pharmacist_user,
            licence_number="PH12345",
            pharmacy_name="City Pharmacy")

    def test_patient_login_view(self):
        response = self.client.get(reverse('patient_login'))
        self.assertEqual(response.status_code, 200)

        # Test successful login redirects to 2FA
        response = self.client.post(reverse('patient_login'), {
            'email': 'patient@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_login_2fa'))

    def test_doctor_login_view(self):
        response = self.client.get(reverse('doctor_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('doctor_login'), {
            'email': 'doctor@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('doctor_login_2fa'))

    def test_pharmacist_login_view(self):
        response = self.client.get(reverse('pharmacist_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('pharmacist_login'), {
            'email': 'pharmacist@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pharmacist_login_2fa'))

    def test_dashboard_access(self):
        # Test patient dashboard access
        self.client.force_login(self.patient_user)
        response = self.client.get(reverse('patient_dash'))
        self.assertEqual(response.status_code, 200)

        # Test doctor dashboard access
        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse('doctor_dash'))
        self.assertEqual(response.status_code, 200)

        # Test pharmacist dashboard access
        self.client.force_login(self.pharmacist_user)
        response = self.client.get(reverse('pharmacist_dash'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_access_denied(self):
        # Patient trying to access doctor dashboard
        self.client.force_login(self.patient_user)
        response = self.client.get(reverse('doctor_dash'))
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Doctor trying to access pharmacist dashboard
        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse('pharmacist_dash'))
        self.assertEqual(response.status_code, 302)