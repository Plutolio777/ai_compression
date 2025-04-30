from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(
        max_length=7,
        error_messages={
            'invalid': '颜色格式必须为#FFFFFF或#FFF'
        }
    )
    
    class Meta:
        model = Tag
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'name': {
                'error_messages': {
                    'blank': '标签名称不能为空',
                    'max_length': '名称长度不能超过20个字符'
                }
            }
        }

    def validate_color(self, value):
        import re
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise serializers.ValidationError("颜色格式必须为#FFFFFF或#FFF")
        return value
