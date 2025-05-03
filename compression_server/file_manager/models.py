from django.db import models
from django.core.validators import MinValueValidator
from tag_manager.models import Tag
import hashlib
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class File(models.Model):
    FILE_TYPES = [
        ('folder', '文件夹'),
        ('file', '文件')
    ]
    tags = models.ManyToManyField('tag_manager.Tag', through='FileTag', related_name='files')
    COMPRESSION_ALGORITHMS = [
        ('zstd', 'Zstandard'),
        ('gzip', 'GZIP'), 
        ('lz4', 'LZ4')
    ]
    STORAGE_TYPES = [
        ('standard', '标准存储'),
        ('hive', 'Hive'),
        ('hbase', 'HBase'),
        ('cloud', '云端存储')
    ]
    
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    actual_file = models.FileField(upload_to='get_user_file_path', null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    compression_algorithm = models.CharField(max_length=20, choices=COMPRESSION_ALGORITHMS, null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES, default='standard')
    storage_path = models.CharField(max_length=512, blank=True, null=True, 
                                  help_text="离线存储系统中的文件路径")
    storage_key = models.CharField(max_length=255, blank=True, null=True,
                                 help_text="存储系统中的文件唯一标识")
    cloud_url = models.URLField(max_length=512, blank=True, null=True,
                              help_text="云端存储的文件URL")
    size = models.BigIntegerField(validators=[MinValueValidator(0)], default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    path_hash = models.CharField(max_length=32, unique=True, editable=False, default='')
    last_downloaded = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        ordering = ['-modified_at']
        indexes = [
            models.Index(fields=['user', 'parent']),
            models.Index(fields=['storage_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_file_type_display()})"

    def get_full_path(self):
        """获取文件/文件夹的完整路径"""
        path_components = []
        current = self.parent
        while current:
            path_components.insert(0, current.name)
            current = current.parent
        return '/'.join(path_components + [self.name])

    def save(self, *args, **kwargs):
        """重写save方法自动计算path_hash"""
        if not self.path_hash:
            full_path = self.get_full_path()
            self.path_hash = hashlib.md5(full_path.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

class FileTag(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('file', 'tag')
        ordering = ['-created_at']

@receiver(post_save, sender=FileTag)
def update_tag_file_count_on_save(sender, instance, **kwargs):
    instance.tag.update_file_count()

@receiver(post_delete, sender=FileTag)
def update_tag_file_count_on_delete(sender, instance, **kwargs):
    instance.tag.update_file_count()

def get_user_file_path(instance, filename):
    # 生成形如：user_<id>/folder1/folder2/filename
    path_components = []
    current = instance.parent
    while current:
        path_components.insert(0, current.name)
        current = current.parent
    return f"user_{instance.user.id}/{'/'.join(path_components)}/{filename}" if path_components else f"user_{instance.user.id}/{filename}"
