from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from django.conf.urls import url
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from .views import (
    ClientViewSet,
    ContractViewSet,
    EventViewSet,
    UserViewSet,
    NotesViewSet,
)

router = SimpleRouter()

router.register("clients", ClientViewSet, basename="clients")
router.register("contracts", ContractViewSet, basename="contracts")
router.register("events", EventViewSet, basename="events")
router.register("users", UserViewSet, basename="users")

events_router = routers.NestedSimpleRouter(router, r"events", lookup="event")
events_router.register(r"notes", NotesViewSet, basename="notes")

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/refresh", TokenRefreshView.as_view(), name="refresh"),
    url(r"^", include(router.urls)),
    url(r"^", include(events_router.urls)),
]
