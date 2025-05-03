from rest_framework import serializers
from .models import ModelConfig, ModelCallRecord
from django.contrib.auth import get_user_model

User = get_user_model()

class ModelConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelConfig
        fields = [
            'id', 'model_type', 'api_key', 'endpoint', 
            'temperature', 'max_tokens', 'is_connected'
        ]


    def validate_temperature(self, value):
        if value < 0 or value > 1.5:
            raise serializers.ValidationError("温度值必须在0到1之间")
        return value

    def validate_max_tokens(self, value):
        if value < 100 or value > 10280:
            raise serializers.ValidationError("最大Token数必须在100到4096之间")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        model_type = validated_data['model_type']
        instance, created = ModelConfig.objects.update_or_create(
            user=user,
            model_type=model_type,
            defaults=validated_data
        )
        return instance

class ModelCallRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCallRecord
        fields = ['id', 'called_at', 'response_time', 'success', 'error_message']
