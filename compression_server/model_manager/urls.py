from django.urls import path
from .views import ModelConfigView, TestConnectionView, CallRecordsView

urlpatterns = [
    path('config/', ModelConfigView.as_view(), name='model-config'),
    path('test-connection/', TestConnectionView.as_view(), name='test-connection'),
    path('call-records/', CallRecordsView.as_view(), name='call-records'),
]
