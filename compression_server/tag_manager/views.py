from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Tag
from .serializers import TagSerializer
from .pagination import StandardPagination

class TagFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    color = filters.CharFilter()
    importance = filters.NumberFilter()

    class Meta:
        model = Tag
        fields = ['name', 'color', 'importance']

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-created_at')
    serializer_class = TagSerializer
    pagination_class = StandardPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TagFilter

    @action(detail=False, methods=['get'])
    def all(self, request):
        """获取所有标签(不分页)"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
