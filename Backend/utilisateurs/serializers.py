from rest_framework import serializers
from .models import BasicUser


class BasicuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicUser
        fields = ['first_name', 'last_name', 'email', 'date_birth', 'phone_number']


class PatientSerializer(BasicUserSerializer):
    class Meta(BasicUserSerializer.Meta):
        fields = BasicUserSerializer.Meta.fields + ['weight', 'blood_type', 'allergies']

    
class DoctorSerializer(BasicUserSerializer):
    class Meta(BasicUserSerializer.Meta):
        fields = BasicUserSerializer.Meta.fields + ['licence_number', 'specialisation']

    
class PharmacistSerializer(BasicUserSerializer):
    class Meta(BasicUserSerializer.Meta):
        fields = BasicUserSerializer.Meta.fields + ['licence_number', 'pharmacy_name']