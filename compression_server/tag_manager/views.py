from rest_framework import viewsets
from .models import Tag
from .serializers import TagSerializer
from .pagination import StandardPagination

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-created_at')
    serializer_class = TagSerializer
    pagination_class = StandardPagination
