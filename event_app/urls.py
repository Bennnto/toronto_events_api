from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, healthz, readyz

router = DefaultRouter()
router.register(r'event', EventViewSet, basename='evnet')

urlpatterns = [
    path('healthz/', healthz, name="healthz"),
    path('readyz/', readyz, name="readyz"),
    path('', include(router.urls)),
]