from rest_framework import serializers
from .models import Blog, Post, Tag
from django.contrib.auth.models import User
from .utils import authenticate_user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm']

    def validate(self, attrs):
        password = attrs.pop('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate_user(username, password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide username and password')
        return attrs

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
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Blog
        fields = ["id", "title", "description", "created_at", "updated_at", "user"]
        read_only_fields = ["created_at", "updated_at"]