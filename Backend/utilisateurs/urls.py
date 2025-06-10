from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('login/2fa/', views.login_2fa, name='login_2fa'),
    path('account/2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('account/2fa/backup-codes/', views.backup_codes, name='backup_codes'),
]