from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Strategy
from .serializers import StrategySerializer
from account.models import User

class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的策略"""
        queryset = self.queryset.filter(user=self.request.user)
        # 确保返回的数据包含完整的配置信息
        if not queryset.exists():
            # 如果没有策略，创建一个默认策略
            Strategy.objects.create(
                user=self.request.user,
                config={
                    'compression': {
                        'name': '默认压缩策略',
                        'description': '默认压缩策略描述',
                        'rules': []
                    },
                    'archive': {
                        'name': '默认归档策略',
                        'description': '默认归档策略描述',
                        'period': 7,
                        'isArchiveOnly': False
                    }
                }
            )
            queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        """创建策略"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """重定向到save_all_strategies方法"""
        return self.save_all_strategies(request)

    def list(self, request, *args, **kwargs):
        """重写list方法确保返回正确的数据结构"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 确保至少有一个策略
        if not queryset.exists():
            Strategy.objects.create(
                user=request.user,
                config={
                    'compression': {
                        'name': '默认压缩策略',
                        'description': '默认压缩策略描述', 
                        'rules': []
                    },
                    'archive': {
                        'name': '默认归档策略',
                        'description': '默认归档策略描述',
                        'period': 7,
                        'isArchiveOnly': False
                    }
                }
            )
            queryset = self.filter_queryset(self.get_queryset())
        
        # 获取第一个策略(每个用户只保留一个策略配置)
        strategy = queryset.first()
        return Response({
            'success': True,
            'data': strategy.config
        })

    def save_all_strategies(self, request):
        """保存所有策略（压缩和归档）"""
        data = request.data
        if not data.get('compression') or not data.get('archive'):
            return Response(
                {'error': '必须提供压缩和归档策略配置'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查找或创建策略
        strategy, created = Strategy.objects.get_or_create(
            user=request.user,
            defaults={'config': data}
        )

        if not created:
            strategy.config = data
            strategy.save()

        return Response({
            'success': True,
            'data': strategy.config
        })
