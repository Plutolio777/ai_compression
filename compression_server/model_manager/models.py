from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ModelConfig(models.Model):
    MODEL_TYPES = (
        ('deepseek', 'DeepSeek'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='model_configs')
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    api_key = models.CharField(max_length=255, blank=True)
    endpoint = models.URLField(max_length=255, blank=True)
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2048)
    sub_model = models.CharField(max_length=50, blank=True, default='')
    is_connected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'model_type')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username}'s {self.model_type} config"

class ModelCallRecord(models.Model):
    config = models.ForeignKey(ModelConfig, on_delete=models.CASCADE, related_name='call_records')
    called_at = models.DateTimeField(auto_now_add=True)
    response_time = models.IntegerField()  # in ms
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-called_at']
