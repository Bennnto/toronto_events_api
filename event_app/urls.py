from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AdminEventViewSet, EventViewSet, healthz, home, readyz,
                    user_login, user_logout, user_register)

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"admin/events", AdminEventViewSet, basename="admin_events")

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/healthz/", healthz, name="healthz"),
    path("api/v1/readyz/", readyz, name="readyz"),
    path("login/", user_login, name="login"),
    path("register/", user_register, name="register"),
    path("logout/", user_logout, name="logout"),
    path("", home, name="home"),
]
