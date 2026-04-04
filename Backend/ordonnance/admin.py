from django.contrib import admin
from .models import Ordonnance


@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_last_name', 'patient_first_name', 'doctor', 'status', 'date_creation')
    list_filter = ('status', 'date_creation')
    search_fields = ('patient_last_name', 'patient_first_name', 'patient_email', 'access_code')
    readonly_fields = ('date_creation', 'access_code', 'signature', '_encrypted_data')
    ordering = ('-date_creation',)
