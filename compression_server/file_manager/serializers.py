from rest_framework import serializers
from .models import File, FileTag
from tag_manager.serializers import TagSerializer

class FileSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'importance': tag.importance
            }
            for tag in obj.tags.all()
        ]
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    storage_type_display = serializers.CharField(source='get_storage_type_display', read_only=True)
    modified_time = serializers.SerializerMethodField()
    important = serializers.SerializerMethodField()
    cold = serializers.SerializerMethodField()
    
    def get_modified_time(self, obj):
        return obj.modified_at.strftime('%Y-%m-%d %H:%M')
        
    def get_important(self, obj):
        return obj.tags.filter(name='important').exists()
        
    def get_cold(self, obj):
        return obj.tags.filter(name='cold').exists()
    
    class Meta:
        model = File
        fields = [
            'id', 'name', 'file_type', 'file_type_display', 
            'is_compressed', 'compression_algorithm', 'compression_ratio',
            'is_archived', 'storage_type', 'storage_type_display',
            'storage_path', 'storage_key', 'cloud_url',
            'size', 'created_at', 'modified_at', 'modified_time',
            'important', 'cold', 'tags'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

class FileTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTag
        fields = ['id', 'file', 'tag', 'created_at']
        read_only_fields = ['id', 'created_at']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    parent_id = serializers.IntegerField(required=False, allow_null=True)

class FolderCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    parent_id = serializers.IntegerField(required=False, allow_null=True)
