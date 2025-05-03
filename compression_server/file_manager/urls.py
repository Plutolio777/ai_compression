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
    path('<int:pk>/get_tags/', FileViewSet.as_view({'get': 'get_tags'}), name='file-get-tags'),
    path('<int:pk>/add_tags/', FileViewSet.as_view({'post': 'add_tags'}), name='file-add-tags'),
    path('<int:pk>/remove_tag/', FileViewSet.as_view({'delete': 'remove_tag'}), name='file-remove-tag'),
    path('<int:pk>/download/', FileViewSet.as_view({'get': 'download'}), name='file-download'),

]
