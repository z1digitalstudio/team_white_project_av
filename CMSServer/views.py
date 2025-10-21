from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Blog, Post, Tag
from .serializers import BlogSerializer, PostSerializer, TagSerializer
from .mixins import PostEditorMixin, LimitBlogChoicesToOwnerMixin, PostOwnerQuerysetViewSetMixin, FilterPostsByBlogViewSetMixin

class BlogViewSet(viewsets.ModelViewSet, LimitBlogChoicesToOwnerMixin):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]


class PostViewSet(
    FilterPostsByBlogViewSetMixin, 
    PostOwnerQuerysetViewSetMixin, 
    PostEditorMixin, 
    viewsets.ModelViewSet
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]