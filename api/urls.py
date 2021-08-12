from rest_framework.routers import SimpleRouter

from .views import ClientViewSet, ContractViewSet, EventViewSet

router = SimpleRouter()

router.register("clients", ClientViewSet, basename="clients")
router.register("contracts", ContractViewSet, basename="contracts")
router.register("events", EventViewSet, basename="events")

urlpatterns = router.urls
