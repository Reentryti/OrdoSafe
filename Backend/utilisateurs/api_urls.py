from django.urls import path
from .api_views import (
    CSRFTokenView,
    DoctorAPILoginView, PharmacistAPILoginView, PatientAPILoginView,
    APIVerify2FAView, APISetup2FAView,
    DoctorAPISignupView, PharmacistAPISignupView,
    APICurrentUserView, APILogoutView,
)

urlpatterns = [
    path('csrf/', CSRFTokenView.as_view(), name='api_csrf'),
    path('me/', APICurrentUserView.as_view(), name='api_current_user'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),

    # Auth
    path('doctor/login/', DoctorAPILoginView.as_view(), name='api_doctor_login'),
    path('pharmacist/login/', PharmacistAPILoginView.as_view(), name='api_pharmacist_login'),
    path('patient/login/', PatientAPILoginView.as_view(), name='api_patient_login'),
    path('verify-2fa/', APIVerify2FAView.as_view(), name='api_verify_2fa'),
    path('setup-2fa/', APISetup2FAView.as_view(), name='api_setup_2fa'),

    # Signup
    path('doctor/signup/', DoctorAPISignupView.as_view(), name='api_doctor_signup'),
    path('pharmacist/signup/', PharmacistAPISignupView.as_view(), name='api_pharmacist_signup'),
]
