from rest_framework import generics
from .models import Tag
from .serializers import TagSerializer
from .pagination import StandardPagination

class TagListCreateView(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Tag.objects.all().order_by('-created_at')

class TagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TagSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        return Tag.objects.all()
