from django.urls import path
from . import views

urlpatterns = [
    path('account/2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('account/2fa/backup-codes/', views.backup_codes, name='backup_codes'),

    path('patient/login/', views.patient_login, name='patient_login'),
    path('patient/login/2fa/', views.patient_login_2fa, name='patient_login_2fa'),
    path('patient/signup/', views.patient_signup, name='patient_signup'),

    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('doctor/login/2fa', views.doctor_login_2fa, name='doctor_login_2fa'),
    path('doctor/signup', views.doctor_signup, name='doctor_signup'),

    path('pharmacist/login', views.pharmacist_login, name='pharmacist_login'),
    path('pharmacist/login_2fa', views.pharmacist_login_2fa, name='pharmacist_login_2fa'),
    path('pharmacist/signup', views.pharmacist_signup, name='pharmacist_signup'),
]