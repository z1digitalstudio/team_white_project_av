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
from blog.constants import (
    AUTH_NOT_AUTHENTICATED,
    BLOG_TITLE_REQUIRED,
    BLOG_DESCRIPTION_REQUIRED,
    BLOG_CREATED_SUCCESS,
    BLOG_UPDATED_SUCCESS,
    BLOG_DELETED_SUCCESS,
    BLOG_NOT_FOUND,
    BLOG_UPDATE_PERMISSION_DENIED,
    BLOG_DELETE_PERMISSION_DENIED,
    BLOG_ERROR_FETCHING,
    BLOG_ERROR_FETCHING_BY_ID,
    BLOG_ERROR_CREATING,
    BLOG_ERROR_UPDATING,
    BLOG_ERROR_DELETING,
    POST_TITLE_REQUIRED,
    POST_CONTENT_REQUIRED,
    POST_CREATED_SUCCESS,
    POST_UPDATED_SUCCESS,
    POST_DELETED_SUCCESS,
    POST_NOT_FOUND,
    POST_UPDATE_PERMISSION_DENIED,
    POST_DELETE_PERMISSION_DENIED,
    POST_MODIFY_PERMISSION_DENIED,
    POST_ERROR_FETCHING,
    POST_ERROR_FETCHING_BY_ID,
    POST_ERROR_CREATING,
    POST_ERROR_UPDATING,
    POST_ERROR_DELETING,
    TAG_NOT_FOUND,
    TAG_ADDED_TO_POST_SUCCESS,
    TAG_REMOVED_FROM_POST_SUCCESS,
    TAG_ERROR_ADDING_TO_POST,
    TAG_ERROR_REMOVING_FROM_POST,
)

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
            raise BaseAPIException(f"{BLOG_ERROR_FETCHING}: {e}")

    def resolve_blog(self, info, id):
        try:
            return Blog.objects.get(id=id)
        except Exception as e:
            raise BaseAPIException(f"{BLOG_ERROR_FETCHING_BY_ID}: {e}")

    def resolve_blogs_by_user(self, info, user_id):
        try:
            return Blog.filter_blogs_by_user(Blog.objects.all(), user_id)
        except Exception as e:
            raise BaseAPIException(f"{BLOG_ERROR_FETCHING}: {e}")

    def resolve_blogs_by_title(self, info, title):
        try:
            return Blog.filter_blogs_by_title(Blog.objects.all(), title)
        except Exception as e:
            raise BaseAPIException(f"{BLOG_ERROR_FETCHING}: {e}")

    def resolve_posts(self, info):
        try:
            return Post.objects.all()
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_FETCHING}: {e}")

    def resolve_post(self, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise NotFoundError(POST_NOT_FOUND)
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_FETCHING_BY_ID}: {e}")
    
    def resolve_posts_by_blog(self, info, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
            return blog.posts.all()
        except Blog.DoesNotExist:
            raise NotFoundError(BLOG_NOT_FOUND)
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_FETCHING}: {e}")

    def resolve_posts_by_user(self, info, user_id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            return Post.objects.filter(blog__user=user)
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_FETCHING}: {e}")

    def resolve_posts_by_title(self, info, title):
        try:
            return Post.objects.filter(title__icontains=title)
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_FETCHING}: {e}")

    

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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            if not title.strip():
                raise BaseAPIException(BLOG_TITLE_REQUIRED)
            if not description.strip():
                raise BaseAPIException(BLOG_DESCRIPTION_REQUIRED)

            blog = Blog.objects.create(title=title, description=description, user=user)
            return CreateBlog(blog=blog, message=BLOG_CREATED_SUCCESS, success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{BLOG_ERROR_CREATING}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                blog = Blog.objects.get(id=id)
            except Blog.DoesNotExist:
                raise NotFoundError(BLOG_NOT_FOUND)

            if not (is_superuser(user) or blog.user == user):
                raise PermissionDeniedError(BLOG_UPDATE_PERMISSION_DENIED)

            if not title.strip():
                raise BaseAPIException(BLOG_TITLE_REQUIRED)
            if not description.strip():
                raise BaseAPIException(BLOG_DESCRIPTION_REQUIRED)

            blog.title = title
            blog.description = description
            blog.save()
            return UpdateBlog(blog=blog, message=BLOG_UPDATED_SUCCESS, success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{BLOG_ERROR_UPDATING}: {e}")


class DeleteBlog(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                blog = Blog.objects.get(id=id)
            except Blog.DoesNotExist:
                raise NotFoundError(BLOG_NOT_FOUND)

            if not (is_superuser(user) or blog.user == user):
                raise PermissionDeniedError(BLOG_DELETE_PERMISSION_DENIED)

            blog.delete()
            return DeleteBlog(message=BLOG_DELETED_SUCCESS, success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{BLOG_ERROR_DELETING}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                blog = Blog.objects.get(id=blog_id)
            except Blog.DoesNotExist:
                raise NotFoundError(BLOG_NOT_FOUND)

            if not title.strip():
                raise BaseAPIException(POST_TITLE_REQUIRED)
            if not content.strip():
                raise BaseAPIException(POST_CONTENT_REQUIRED)

            post = Post.objects.create(blog=blog, title=title, content=content)
            return CreatePost(post=post, message=POST_CREATED_SUCCESS, success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_CREATING}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                post = Post.objects.get(id=id)
            except Post.DoesNotExist:
                raise NotFoundError(POST_NOT_FOUND)

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError(POST_UPDATE_PERMISSION_DENIED)

            if not title.strip():
                raise BaseAPIException(POST_TITLE_REQUIRED)
            if not content.strip():
                raise BaseAPIException(POST_CONTENT_REQUIRED)

            post.title = title
            post.content = content
            post.save()
            return UpdatePost(post=post, message=POST_UPDATED_SUCCESS, success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_UPDATING}: {e}")


class DeletePost(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                post = Post.objects.get(id=id)
            except Post.DoesNotExist:
                raise NotFoundError(POST_NOT_FOUND)

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError(POST_DELETE_PERMISSION_DENIED)

            post.delete()
            return DeletePost(message=POST_DELETED_SUCCESS, success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{POST_ERROR_DELETING}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFoundError(POST_NOT_FOUND)

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError(POST_MODIFY_PERMISSION_DENIED)

            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise NotFoundError(TAG_NOT_FOUND)

            post.tags.add(tag)
            return AddTagToPost(post=post, tag=tag, message=TAG_ADDED_TO_POST_SUCCESS, success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_ADDING_TO_POST}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFoundError(POST_NOT_FOUND)

            if not (is_superuser(user) or post.blog.user == user):
                raise PermissionDeniedError(POST_MODIFY_PERMISSION_DENIED)

            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise NotFoundError(TAG_NOT_FOUND)

            post.tags.remove(tag)
            return RemoveTagFromPost(post=post, tag=tag, message=TAG_REMOVED_FROM_POST_SUCCESS, success=True)

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_REMOVING_FROM_POST}: {e}")

class Mutation(graphene.ObjectType):
    create_blog = CreateBlog.Field()
    update_blog = UpdateBlog.Field()
    delete_blog = DeleteBlog.Field()
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    add_tag_to_post = AddTagToPost.Field()
    remove_tag_from_post = RemoveTagFromPost.Field()
