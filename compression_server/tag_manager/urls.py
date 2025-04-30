from django.urls import path
from . import views

app_name = 'tag_api'

urlpatterns = [
    path('', views.TagListCreateView.as_view(), name='tag-list'),
    path('<int:pk>/', views.TagRetrieveUpdateDestroyView.as_view(), name='tag-detail'),
]
