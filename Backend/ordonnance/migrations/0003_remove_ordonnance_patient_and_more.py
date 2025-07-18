# Generated by Django 5.2.4 on 2025-07-11 17:56

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordonnance', '0002_alter_ordonnance_doctor_alter_ordonnance_patient'),
        ('utilisateurs', '0007_remove_basicuser_email_hash_alter_basicuser_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordonnance',
            name='patient',
        ),
        migrations.AddField(
            model_name='ordonnance',
            name='patient_date_naissance',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordonnance',
            name='patient_email',
            field=models.EmailField(blank=True, db_index=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='ordonnance',
            name='patient_nom',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ordonnance',
            name='patient_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=128, null=True, region='SN', unique=True),
        ),
        migrations.AddField(
            model_name='ordonnance',
            name='patient_prenom',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='ordonnance',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordonnances_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ordonnance',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordonnances', to='utilisateurs.doctor'),
        ),
    ]
