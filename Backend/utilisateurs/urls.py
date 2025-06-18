from django.urls import path
from . import views
from .views import (
    PatientSignUpView, PatientLoginView, PatientLogin2faView,
    DoctorSignUpView, DoctorLoginView, DoctorLogin2faView,
    PharmacistSignUpView, PharmacistLoginView, PharmacistLogin2faView
)

urlpatterns = [
    path('account/2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('account/2fa/backup-codes/', views.backup_codes, name='backup_codes'),

    path('patient/login/', PatientLoginView.as_view(), name='patient_login'),
    path('patient/login/2fa/', PatientLogin2faView.as_view(), name='patient_login_2fa'),
    path('patient/signup/', PatientSignUpView.as_view(), name='patient_signup'),

    path('doctor/login/', DoctorLoginView.as_view(), name='doctor_login'),
    path('doctor/login/2fa/', DoctorLogin2faView.as_view(), name='doctor_login_2fa'),
    path('doctor/signup/', DoctorSignUpView.as_view(), name='doctor_signup'),

    path('pharmacist/login', PharmacistLoginView.as_view(), name='pharmacist_login'),
    path('pharmacist/login_2fa/', PharmacistLogin2faView.as_view(), name='pharmacist_login_2fa'),
    path('pharmacist/signup', PharmacistSignUpView.as_view(), name='pharmacist_signup'),
]