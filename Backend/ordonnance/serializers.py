from rest_framework import serializers
from .models import Ordonnance, Medicament

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = '__all__'

class OrdonnanceSerializer(serializers.ModelSerializer):
    medicaments = MedicamentSerializer(many=True)

    class Meta:
        model = Ordonnance
        fields = '__all__'

    def create(self, validated_data):
        medicaments_data = validated_data.pop('medicaments')
        ordonnance = Ordonnance.objects.create(**validated_data)
        for med_data in medicaments_data:
            med = Medicament.objects.create(**med_data)
            ordonnance.medicaments.add(med)
        return ordonnance