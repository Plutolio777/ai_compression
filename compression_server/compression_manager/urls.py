from django.urls import path
from .views import FileUploadView, CompressionAnalysisView, TaskStatusView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('analyze/', CompressionAnalysisView.as_view(), name='compression-analyze'),
    path('task/<uuid:task_id>/', TaskStatusView.as_view(), name='task-status'),
]
