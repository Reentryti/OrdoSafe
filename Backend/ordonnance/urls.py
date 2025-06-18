from rest_framework.routers import DefaultRouter
from .views import OrdonnanceViewSet, MedicamentViewSet

router = DefaultRouter()
router.register(r'ordonnances', OrdonnanceViewSet)
router.register(r'medicaments', MedicamentViewSet)

urlpatterns = router.urls