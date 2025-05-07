from django.db import models
from account.models import User
import uuid

class Strategy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strategies')
    config = models.JSONField()  # 存储压缩和归档策略配置
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '策略配置'
        verbose_name_plural = '策略配置'

    def __str__(self):
        return f'用户 {self.user.username} 的策略配置'
