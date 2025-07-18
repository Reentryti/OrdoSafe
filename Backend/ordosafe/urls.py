"""
URL configuration for ordosafe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

urlpatterns = [

    path('', home, name='home'),
    # Admin URL
    # This is the URL for the Django admin interface
    path('admin/', admin.site.urls),
    # Include the URLs from the utilisateurs app
    # This allows us to manage user accounts, including login, signup, and 2FA setup
    path('api/', include('utilisateurs.urls')),
    # Include the URLs for Django Allauth
    # This is used for user authentication, registration, and social account management
    #path('accounts/', include('allauth.urls')), 
    path('ordonnance/', include('ordonnance.urls', namespace='ordonnance')),
]
