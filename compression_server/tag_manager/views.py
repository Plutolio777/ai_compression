from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import Tag
from .serializers import TagSerializer
from .pagination import StandardPagination

class TagFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    color = filters.CharFilter()

    class Meta:
        model = Tag
        fields = ['name', 'color']

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-created_at')
    serializer_class = TagSerializer
    pagination_class = StandardPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TagFilter
