from rest_framework.routers import SimpleRouter

from .views import ClientViewSet, ContractViewSet, EventViewSet, UserViewSet

router = SimpleRouter()

router.register("clients", ClientViewSet, basename="clients")
router.register("contracts", ContractViewSet, basename="contracts")
router.register("events", EventViewSet, basename="events")
router.register("users", UserViewSet, basename="users")

urlpatterns = router.urls
