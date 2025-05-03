from rest_framework import serializers
from .models import CompressionTask, TempUploadedFile


class TempUploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempUploadedFile
        fields = ['id', 'original_name', 'size', 'upload_time', 'status']

class CompressionTaskSerializer(serializers.ModelSerializer):
    files = TempUploadedFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = CompressionTask
        fields = ['id', 'created_at', 'status', 'analysis_result', 'files']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    task_id = serializers.UUIDField()

    def create(self, validated_data):
        task_id = validated_data['task_id']
        file = validated_data['file']
        
        task, created = CompressionTask.objects.get_or_create(id=task_id)
        
        uploaded_file = TempUploadedFile.objects.create(
            task=task,
            file=file,
            original_name=file.name,
            size=file.size
        )
        
        return uploaded_file


    task_id = serializers.UUIDField()

    def analyze_files(self):
        task_id = self.validated_data['task_id']
        try:
            task = CompressionTask.objects.get(id=task_id)
            files = task.files.all()
            
            # 准备文件信息给AI分析
            file_data = [
                {
                    'index': idx,
                    'name': file.original_name,
                    'size': file.size,
                    'type': os.path.splitext(file.original_name)[1][1:].upper()
                }
                for idx, file in enumerate(files)
            ]
            
            # 调用AI分析
            invoker = ModelInvoker.get_instance()
            result = invoker.decision_intelligence(file_data)
            
            # 保存分析结果
            task.analysis_result = result
            task.status = 'completed'
            task.save()
            
            return result
        except CompressionTask.DoesNotExist:
            raise serializers.ValidationError('任务不存在')
