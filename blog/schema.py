"""
import graphene
from graphene_django import DjangoObjectType
from .models import Blog, Post
from user.schema import UserType
from user.utils import get_authenticated_user
from user.exceptions import AuthenticationError, PermissionDeniedError
from blog.mixins import PostEditorMixin

class BlogType(DjangoObjectType):
    class Meta:
        model = Blog
        fields = "__all__"

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"

class Query(graphene.ObjectType):
    all_blogs = graphene.List(BlogType)
    all_posts = graphene.List(PostType)
    blog_by_id = graphene.Field(BlogType, id=graphene.ID())
    post_by_id = graphene.Field(PostType, id=graphene.ID())

    def resolve_all_blogs(self, info):
        return Blog.objects.all()

    def resolve_all_posts(self, info):
        return Post.objects.all()

    def resolve_blog_by_id(self, info, id):
        return Blog.objects.get(id=id)

    def resolve_post_by_id(self, info, id):
        return Post.objects.get(id=id)

class CreateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)

    def mutate(self, info, title, description):
        current_user = get_authenticated_user(info)
        if not current_user.is_authenticated:
            raise AuthenticationError("You are not authenticated")

        blog = Blog.objects.create(title=title, description=description, user=current_user)
        return CreateBlog(blog=blog, message="Blog created successfully", success=True)

class UpdateBlog(graphene.Mutation, PostEditorMixin):

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)

    def mutate(self, info, id, title, description):
        current_user = get_authenticated_user(info)
        if not current_user.is_authenticated:
            raise AuthenticationError("You are not authenticated")

        blog = Blog.objects.get(id=id)
        

        blog.title = title
        blog.description = description
        blog.save()
        return UpdateBlog(blog=blog, message="Blog updated successfully", success=True)

class DeleteBlog(graphene.Mutation, PostEditorMixin):

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        current_user = get_authenticated_user(info)
        if not current_user.is_authenticated:
            raise AuthenticationError("You are not authenticated")

        blog = Blog.objects.get(id=id)
       
        blog.delete()
        return DeleteBlog(message="Blog deleted successfully", success=True)

class Mutation(graphene.ObjectType):
    create_blog = CreateBlog.Field()
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
"""