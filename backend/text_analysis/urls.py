from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextAnalysisViewSet

router = DefaultRouter()
router.register(r'analysis', TextAnalysisViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]