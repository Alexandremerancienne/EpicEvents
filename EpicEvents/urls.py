from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("crm/v1/", include("crm.urls")),
    path("crm-auth/", include("rest_framework.urls")),
]
