from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Blog, Post, Tag
from .serializers import BlogSerializer, PostSerializer, TagSerializer
from .mixins import PostEditorMixin, LimitBlogChoicesToOwnerMixin, PostOwnerQuerysetViewSetMixin, FilterPostsByBlogViewSetMixin
from django.contrib.auth import login, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .serializers import LoginSerializer, UserSerializer
from .mixins import AuthenticationMixin


class AuthViewSet(viewsets.ViewSet, AuthenticationMixin):
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = self.create_user_token(user)
            login(request, user)
            return Response({
                'token': token,
                'user': UserSerializer(user).data,
                'message': 'Login exitoso'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        self.delete_user_token(request.user)
        logout(request)
        return Response({'message': 'Logout exitoso'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class BlogViewSet(viewsets.ModelViewSet, LimitBlogChoicesToOwnerMixin):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostViewSet(
    FilterPostsByBlogViewSetMixin, 
    PostOwnerQuerysetViewSetMixin, 
    PostEditorMixin, 
    viewsets.ModelViewSet
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]