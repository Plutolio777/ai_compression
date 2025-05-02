from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('', include(router.urls)),
    path('tree/', FileViewSet.as_view({'get': 'tree'}), name='file-tree'),
    path('upload/', FileViewSet.as_view({'post': 'upload'}), name='file-upload'),
    path('create_folder/', FileViewSet.as_view({'post': 'create_folder'}), name='create-folder'),
]
