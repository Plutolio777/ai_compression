from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import File, FileTag
from tag_manager.models import Tag
from .serializers import (
    FileSerializer, 
    FileTagSerializer,
    FileUploadSerializer,
    FolderCreateSerializer
)
from tag_manager.serializers import TagSerializer
from account.models import User

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        path = self.request.query_params.get('path', '')
        
        # 获取当前路径下的文件和文件夹
        if path:
            path_parts = path.split('/')
            parent = None
            for part in path_parts:
                if not part:
                    continue
                try:
                    parent = File.objects.get(
                        user=user,
                        name=part,
                        file_type='folder',
                        parent=parent
                    )
                except File.DoesNotExist:
                    return File.objects.none()
            
            queryset = queryset.filter(user=user, parent=parent)
        else:
            queryset = queryset.filter(user=user, parent__isnull=True)
        
        return queryset.order_by('-modified_at')

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """根据parent_id获取子树结构"""
        user = request.user
        parent_id = request.query_params.get('parent_id')
        
        if parent_id:
            try:
                parent = File.objects.get(id=parent_id, user=user)
                files = File.objects.filter(parent=parent, user=user)
            except File.DoesNotExist:
                return Response({'error': '父文件夹不存在'}, status=status.HTTP_404_NOT_FOUND)
        else:
            files = File.objects.filter(parent__isnull=True, user=user)
            
        data = self._build_file_tree(files)
        return Response(data)

    def _build_file_tree(self, files):
        result = []
        for file in files:
            # 获取文件扩展名识别具体类型
            file_type = file.file_type
            if file_type == 'file':
                ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
                if ext in ['jpg', 'jpeg', 'png', 'gif']:
                    file_type = 'image'
                elif ext == 'pdf':
                    file_type = 'pdf'
                elif ext in ['mp4', 'mov', 'avi']:
                    file_type = 'video'
                elif ext in ['mp3', 'wav']:
                    file_type = 'audio'
                elif ext in ['zip', 'rar', '7z']:
                    file_type = 'archive'
                elif ext in ['doc', 'docx']:
                    file_type = 'doc'
                elif ext in ['xls', 'xlsx']:
                    file_type = 'xls'
                elif ext in ['ppt', 'pptx']:
                    file_type = 'ppt'
                elif ext in ['py', 'js', 'java', 'html', 'css']:
                    file_type = 'code'
                elif ext in ['psd', 'ai']:
                    file_type = ext

            # 获取标签重要性
            important_tags = file.tags.filter(importance__gte=2)
            importance_level = important_tags.first().importance if important_tags.exists() else 1

            node = {
                'id': file.id,
                'name': file.name,
                'type': file_type,
                'size': file.size,
                'modifiedTime': file.modified_at.strftime('%Y-%m-%d %H:%M'),
                'important': important_tags.exists(),
                'importance': importance_level,
                'cold': file.tags.filter(name='cold').exists(),
                'children': []
            }
            if file.file_type == 'folder':
                # 只查询直接子节点，不递归查询
                children = File.objects.filter(parent=file)
                node['children'] = [{
                    'id': child.id,
                    'name': child.name,
                    'type': child.file_type,
                    'size': child.size,
                    'modifiedTime': child.modified_at.strftime('%Y-%m-%d %H:%M'),
                    'important': child.tags.filter(importance__gte=2).exists(),
                    'importance': child.tags.filter(importance__gte=2).first().importance if child.tags.filter(importance__gte=2).exists() else 1,
                    'cold': child.tags.filter(name='cold').exists(),
                    'children': []  # 前端需要时再请求下一级
                } for child in children]
            result.append(node)
        return result

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """文件上传接口"""
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            uploaded_file = serializer.validated_data['file']
            parent_id = serializer.validated_data.get('parent_id')
            
            # 查找父目录
            parent = None
            if parent_id:
                parent = File.objects.get(
                    id=parent_id,
                    user=user,
                    file_type='folder'
                )

            # 创建文件记录
            file = File.objects.create(
                user=user,
                parent=parent,
                name=uploaded_file.name,
                file_type='file',
                actual_file=uploaded_file,
                size=uploaded_file.size
            )

            return Response(FileSerializer(file).data, status=status.HTTP_201_CREATED)
        except File.DoesNotExist:
            return Response(
                {'error': '指定的父目录不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None):
        """为文件添加标签"""
        try:
            file = self.get_object()
            tag_ids = request.data.get('tag_ids', [])
            
            if not tag_ids:
                return Response(
                    {'error': '请提供标签ID列表'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 获取标签对象
            tags = Tag.objects.filter(id__in=tag_ids)
            if tags.count() != len(tag_ids):
                return Response(
                    {'error': '部分标签不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 添加标签关联
            for tag in tags:
                FileTag.objects.get_or_create(file=file, tag=tag)
                tag.file_count = tag.files.count()
                tag.save()
                
            # 重新获取文件数据，包含更新后的标签
            file.refresh_from_db()
            return Response(
                FileSerializer(file).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['delete'])
    def remove_tag(self, request, pk=None):
        """移除文件标签"""
        try:
            file = self.get_object()
            tag_id = request.data.get('tag_id')
            
            if not tag_id:
                return Response(
                    {'error': '请提供标签ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 验证标签是否存在
            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                return Response(
                    {'error': '标签不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 移除标签关联
            FileTag.objects.filter(file=file, tag=tag).delete()
            
            # 更新标签文件数
            tag.update_file_count()
            
            return Response(
                {'success': True},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def get_tags(self, request, pk=None):
        """获取文件标签列表"""
        try:
            file = self.get_object()
            tags = file.tags.all()
            return Response(
                TagSerializer(tags, many=True).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def create_folder(self, request):
        """创建文件夹接口"""
        serializer = FolderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            name = serializer.validated_data['name']
            parent_id = serializer.validated_data.get('parent_id')
            
            # 查找父目录
            parent = None
            if parent_id:
                parent = File.objects.get(
                    id=parent_id,
                    user=user,
                    file_type='folder'
                )

            # 检查同一父目录下同名文件夹是否已存在
            if parent and File.objects.filter(user=user, name=name, parent=parent, file_type='folder').exists():
                return Response(
                    {'error': '当前目录下已存在同名文件夹'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif not parent and File.objects.filter(user=user, name=name, parent__isnull=True, file_type='folder').exists():
                return Response(
                    {'error': '根目录下已存在同名文件夹'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 创建文件夹记录
            folder = File.objects.create(
                user=user,
                parent=parent,
                name=name,
                file_type='folder'
            )

            return Response(FileSerializer(folder).data, status=status.HTTP_201_CREATED)
        except File.DoesNotExist:
            return Response(
                {'error': '指定的父目录不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
