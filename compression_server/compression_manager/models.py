from django.db import models
import uuid
import os

def get_upload_path(instance, filename):
    return os.path.join('temp_uploads', str(instance.task_id), filename)

class CompressionTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败')
    ])
    analysis_result = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'compression_tasks'
        ordering = ['-created_at']

class TempUploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(CompressionTask, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_upload_path)
    original_name = models.CharField(max_length=255)
    size = models.BigIntegerField()
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='uploading', choices=[
        ('uploading', '上传中'),
        ('uploaded', '上传完成'),
        ('failed', '上传失败')
    ])

    class Meta:
        db_table = 'temp_uploaded_files'
        ordering = ['upload_time']
