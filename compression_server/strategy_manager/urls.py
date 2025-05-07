from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StrategyViewSet

router = DefaultRouter()
router.register(r'strategies', StrategyViewSet, basename='strategy')

urlpatterns = [
    path('', include(router.urls)),
    path('strategies/save_all/', 
        StrategyViewSet.as_view({'post': 'save_all_strategies'}),
        name='save-all-strategies'),
]
