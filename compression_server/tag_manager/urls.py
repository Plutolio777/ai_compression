from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tag_api'

router = DefaultRouter()
router.register(r'', views.TagViewSet, basename='tag')

urlpatterns = router.urls
