from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Patient, Doctor, Pharmacist, LoginAttempt

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
        self.assertEqual(self.user.login_attempts, 0)
        self.assertFalse(self.user.is_account_locked())

        self.user.increment_login_attempts()
        self.assertEqual(self.user.login_attempts, 1)
        self.assertFalse(self.user.is_account_locked())

        self.user.increment_login_attempts()
        self.user.increment_login_attempts()
        self.assertTrue(self.user.is_account_locked())

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
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            date_birth=date(1990, 1, 1)
        )
        attempt = LoginAttempt.objects.create(
            user=user,
            username="test@example.com",
            ip_address="127.0.0.1",
            success=True
        )
        self.assertIn("test@example.com", str(attempt))
        self.assertIn("Success", str(attempt))


class AuthViewsTest(TestCase):
    def setUp(self):
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

    def test_doctor_login_post(self):
        response = self.client.post(reverse('doctor_login'), {
            'email': 'doctor@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_pharmacist_login_post(self):
        response = self.client.post(reverse('pharmacist_login'), {
            'email': 'pharmacist@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_dashboard_redirects_wrong_role(self):
        # Doctor trying to access pharmacist dashboard should redirect
        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse('pharmacist_dash'))
        self.assertEqual(response.status_code, 302)

        # Pharmacist trying to access doctor dashboard should redirect
        self.client.force_login(self.pharmacist_user)
        response = self.client.get(reverse('doctor_dash'))
        self.assertEqual(response.status_code, 302)
