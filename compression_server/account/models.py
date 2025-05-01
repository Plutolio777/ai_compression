from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)
    avatar = models.FileField(
        upload_to='avator/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])]
    )
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'mobile']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        return self.username
