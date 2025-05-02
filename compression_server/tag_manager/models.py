from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator

class Tag(models.Model):
    IMPORTANCE_CHOICES = [
        (1, '低'),
        (2, '中'), 
        (3, '高')
    ]
    
    name = models.CharField(
        max_length=20,
        validators=[
            MinLengthValidator(1, message="名称不能为空"),
            RegexValidator(r'^[\w\u4e00-\u9fa5]{1,20}$', message="仅允许中英文、数字和下划线")
        ]
    )
    description = models.TextField(blank=True, max_length=200)
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='颜色格式必须为#FFFFFF或#FFF'
            )
        ]
    )
    importance = models.IntegerField(
        choices=IMPORTANCE_CHOICES,
        default=1,
        verbose_name='重要性'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    file_count = models.PositiveIntegerField(default=0, verbose_name='关联文件数')

    class Meta:
        db_table = 'tag'
        ordering = ['-created_at']

    def update_file_count(self):
        """更新关联文件数"""
        self.file_count = self.file_set.count()
        self.save()
