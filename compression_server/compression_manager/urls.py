from django.urls import path
from .views import FileUploadView, analysis_view, TaskStatusView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('analyze/', analysis_view, name='compression-analyze'),
    # path('task/<uuid:task_id>/', TaskStatusView.as_view(), name='task-status'),
]
