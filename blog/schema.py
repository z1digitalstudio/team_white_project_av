import graphene
from .models import Blog, Post
from tag.models import Tag
from user.utils import get_authenticated_user, is_superuser
from user.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    BaseAPIException,
    NotFoundError,
)
from Core.graphql_types import BlogType, PostType, TagType

class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id=graphene.ID(required=True))

    posts_by_blog = graphene.List(PostType, blog_id=graphene.ID(required=True))
    posts_by_user = graphene.List(PostType, user_id=graphene.ID(required=True))
    posts_by_title = graphene.List(PostType, title=graphene.String(required=True))

    blogs = graphene.List(BlogType)
    blog = graphene.Field(BlogType, id=graphene.ID(required=True))
    blogs_by_user = graphene.List(BlogType, user_id=graphene.ID(required=True))
    blogs_by_title = graphene.List(BlogType, title=graphene.String(required=True))

    def resolve_blogs(self, info):
        try:
            return Blog.objects.all()
        except Exception as e:
            raise BaseAPIException(f"Error fetching blogs: {e}")

    def resolve_blog(self, info, id):
        try:
            return Blog.objects.get(id=id)
        except Exception as e:
            raise BaseAPIException(f"Error fetching blog: {e}")

    def resolve_blogs_by_user(self, info, user_id):
        try:
            return Blog.filter_blogs_by_user(Blog.objects.all(), user_id)
        except Exception as e:
            raise BaseAPIException(f"Error fetching blogs: {e}")

    def resolve_blogs_by_title(self, info, title):
        try:
            return Blog.filter_blogs_by_title(Blog.objects.all(), title)
        except Exception as e:
            raise BaseAPIException(f"Error fetching blogs: {e}")

    def resolve_posts(self, info):
        try:
            return Post.objects.all()
        except Exception as e:
            raise BaseAPIException(f"Error fetching posts: {e}")

    def resolve_post(self, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise NotFoundError("Post not found")
        except Exception as e:
            raise BaseAPIException(f"Error fetching post: {e}")
    
    def resolve_posts_by_blog(self, info, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
            return blog.posts.all()
        except Blog.DoesNotExist:
            raise NotFoundError("Blog not found")
        except Exception as e:
            raise BaseAPIException(f"Error fetching posts: {e}")

    def resolve_posts_by_user(self, info, user_id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            return Post.objects.filter(blog__user=user)
        except Exception as e:
            raise BaseAPIException(f"Error fetching posts: {e}")

    def resolve_posts_by_title(self, info, title):
        try:
            return Post.objects.filter(title__icontains=title)
        except Exception as e:
            raise BaseAPIException(f"Error fetching posts: {e}")

    

class CreateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)

    def mutate(self, info, title, description):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            if not title.strip():
                raise BaseAPIException("Title is required")
            if not description.strip():
                raise BaseAPIException("Description is required")

            blog = Blog.objects.create(title=title, description=description, user=user)
            return CreateBlog(blog=blog, message="Blog created successfully", success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error creating blog: {e}")


class UpdateBlog(graphene.Mutation):
    blog = graphene.Field(BlogType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)

    def mutate(self, info, id, title, description):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                blog = Blog.objects.get(id=id)
            except Blog.DoesNotExist:
                raise NotFoundError("Blog not found")

            if not (is_superuser(user) or blog.user == user):
                raise PermissionDeniedError("You are not allowed to update this blog")

            if not title.strip():
                raise BaseAPIException("Title is required")
            if not description.strip():
                raise BaseAPIException("Description is required")

            blog.title = title
            blog.description = description
            blog.save()
            return UpdateBlog(blog=blog, message="Blog updated successfully", success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error updating blog: {e}")


class DeleteBlog(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                blog = Blog.objects.get(id=id)
            except Blog.DoesNotExist:
                raise NotFoundError("Blog not found")

            if not (is_superuser(user) or blog.user == user):
                raise PermissionDeniedError("You are not allowed to delete this blog")

            blog.delete()
            return DeleteBlog(message="Blog deleted successfully", success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error deleting blog: {e}")


class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        blog_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, blog_id, title, content):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                blog = Blog.objects.get(id=blog_id)
            except Blog.DoesNotExist:
                raise NotFoundError("Blog not found")

            if not title.strip():
                raise BaseAPIException("Title is required")
            if not content.strip():
                raise BaseAPIException("Content is required")

            post = Post.objects.create(blog=blog, title=title, content=content)
            return CreatePost(post=post, message="Post created successfully", success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error creating post: {e}")


class UpdatePost(graphene.Mutation):
    post = graphene.Field(PostType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, id, title, content):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                post = Post.objects.get(id=id)
            except Post.DoesNotExist:
                raise NotFoundError("Post not found")

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError("You are not allowed to update this post")

            if not title.strip():
                raise BaseAPIException("Title is required")
            if not content.strip():
                raise BaseAPIException("Content is required")

            post.title = title
            post.content = content
            post.save()
            return UpdatePost(post=post, message="Post updated successfully", success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error updating post: {e}")


class DeletePost(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                post = Post.objects.get(id=id)
            except Post.DoesNotExist:
                raise NotFoundError("Post not found")

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError("You are not allowed to delete this post")

            post.delete()
            return DeletePost(message="Post deleted successfully", success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error deleting post: {e}")


class AddTagToPost(graphene.Mutation):
    post = graphene.Field(PostType)
    tag = graphene.Field(TagType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        post_id = graphene.ID(required=True)
        tag_id = graphene.ID(required=True)

    def mutate(self, info, post_id, tag_id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFoundError("Post not found")

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError("You are not allowed to modify this post")

            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise NotFoundError("Tag not found")

            post.tags.add(tag)
            return AddTagToPost(post=post, tag=tag, message="Tag added to post successfully", success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error adding tag to post: {e}")


class RemoveTagFromPost(graphene.Mutation):
    post = graphene.Field(PostType)
    tag = graphene.Field(TagType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        post_id = graphene.ID(required=True)
        tag_id = graphene.ID(required=True)

    def mutate(self, info, post_id, tag_id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFoundError("Post not found")

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError("You are not allowed to modify this post")

            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise NotFoundError("Tag not found")

            post.tags.remove(tag)
            return RemoveTagFromPost(post=post, tag=tag, message="Tag removed from post successfully", success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error removing tag from post: {e}")

class Mutation(graphene.ObjectType):
    create_blog = CreateBlog.Field()
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    add_tag_to_post = AddTagToPost.Field()
    remove_tag_from_post = RemoveTagFromPost.Field()
