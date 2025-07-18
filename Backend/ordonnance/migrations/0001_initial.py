# Generated by Django 5.1.4 on 2025-06-22 02:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('utilisateurs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ordonnance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicaments', models.JSONField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('issued', 'Émise'), ('cancelled', 'Annulée'), ('fulfilled', 'Honorée')], default='draft', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('signature', models.TextField(blank=True, null=True)),
                ('_encrypted_data', models.BinaryField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordonnance_created', to=settings.AUTH_USER_MODEL)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordonnance_doctor', to='utilisateurs.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordonnance_patient', to='utilisateurs.patient')),
            ],
        ),
    ]
