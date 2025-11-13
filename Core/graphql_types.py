from graphene_django import DjangoObjectType
from blog.models import Blog, Post
from tag.models import Tag
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class BlogType(DjangoObjectType):
    class Meta:
        model = Blog
        fields = "__all__"


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = "__all__"
