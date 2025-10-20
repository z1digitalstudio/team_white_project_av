from rest_framework import serializers
from .models import Blog, Post, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

class PostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    blog = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Post
        fields = ["id", "title", "content", "published_at", "updated_at", "blog", "tags"]
        read_only_fields = ["published_at", "updated_at", "blog"]

class BlogSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) 
    class Meta:
        model = Blog
        fields = ["id", "title", "description", "created_at", "updated_at", "user"]
        read_only_fields = ["created_at", "updated_at"]
