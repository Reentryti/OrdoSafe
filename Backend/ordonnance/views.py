from rest_framework import viewsets
from .models import Ordonnance, Medicament
from .serializers import OrdonnanceSerializer, MedicamentSerializer

class OrdonnanceViewSet(viewsets.ModelViewSet):
    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceSerializer

class MedicamentViewSet(viewsets.ModelViewSet):
    queryset = Medicament.objects.all()
    serializer_class = MedicamentSerializer