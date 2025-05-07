from rest_framework import serializers
from .models import Strategy
from account.models import User

class StrategySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Strategy
        fields = ['id', 'user', 'config', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_config(self, value):
        """验证配置JSON字段"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("配置必须是JSON对象")
        
        # 验证压缩策略配置
        if 'compression' in value:
            if not isinstance(value['compression'], dict):
                raise serializers.ValidationError("压缩策略配置必须是JSON对象")
            
        # 验证归档策略配置
        if 'archive' in value:
            if not isinstance(value['archive'], dict):
                raise serializers.ValidationError("归档策略配置必须是JSON对象")
            
        return value

    def create(self, validated_data):
        """创建策略"""
        return Strategy.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """更新策略"""
        instance.config = validated_data.get('config', instance.config)
        instance.save()
        return instance
