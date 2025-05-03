from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FileUploadSerializer
from .models import CompressionTask
import uuid

class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.save()
            return Response({
                'success': True,
                'file_id': str(uploaded_file.id),
                'task_id': str(uploaded_file.task.id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompressionAnalysisView(APIView):
    def post(self, request):
        pass

class TaskStatusView(APIView):
    def get(self, request, task_id):
        try:
            task = CompressionTask.objects.get(id=uuid.UUID(task_id))
            return Response({
                'success': True,
                'status': task.status,
                'analysis_result': task.analysis_result
            })
        except CompressionTask.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)
