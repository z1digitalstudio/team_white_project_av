import graphene
from .models import Tag
from user.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    BaseAPIException,
    NotFoundError,
)
from user.utils import get_authenticated_user, is_superuser
from blog.models import Post
from Core.graphql_types import TagType, PostType


class Query(graphene.ObjectType):
    tags = graphene.List(TagType)
    tag = graphene.Field(TagType, id=graphene.ID(required=True))
    posts_by_tag = graphene.List(PostType, id=graphene.ID(required=True))
    tags_by_post = graphene.List(TagType, id=graphene.ID(required=True))
    tags_by_post_name = graphene.List(TagType, post_name=graphene.String(required=True))
    tags_by_name = graphene.List(TagType, name=graphene.String(required=True))
    tags_by_name_and_post_id = graphene.List(
        TagType,
        name=graphene.String(required=True),
        post_id=graphene.ID(required=True),
    )
    tags_by_name_and_post_name = graphene.List(
        TagType,
        name=graphene.String(required=True),
        post_name=graphene.String(required=True),
    )

    def resolve_tags(self, info):
        try:
            return Tag.objects.all()
        except Exception as e:
            raise BaseAPIException(f"Error fetching tags: {e}")

    def resolve_tag(self, info, id):
        try:
            return Tag.objects.get(id=id)
        except Tag.DoesNotExist:
            raise NotFoundError("Tag not found")

    def resolve_posts_by_tag(self, info, id):
        try:
            tag = Tag.objects.get(id=id)
            return tag.posts.all()
        except Tag.DoesNotExist:
            raise NotFoundError("Tag not found")

    def resolve_tags_by_post(self, info, id):
        try:
            post = Post.objects.get(id=id)
            return post.tags.all()
        except Post.DoesNotExist:
            raise NotFoundError("Post not found")

    def resolve_tags_by_post_name(self, info, post_name):
        try:
            post = Post.objects.get(name=post_name)
            return post.tags.all()
        except Post.DoesNotExist:
            raise NotFoundError("Post not found")

    def resolve_tags_by_name(self, info, name):
        try:
            return Tag.objects.filter(name__icontains=name)
        except Exception as e:
            raise BaseAPIException(f"Error filtering tags: {e}")

    def resolve_tags_by_name_and_post_name(self, info, name, post_name):
        try:
            post = Post.objects.get(name=post_name)
            return Tag.objects.filter(name__icontains=name, posts=post)
        except Post.DoesNotExist:
            raise NotFoundError("Post not found")
        except Exception as e:
            raise BaseAPIException(f"Error filtering tags: {e}")

    def resolve_tags_by_name_and_post_id(self, info, name, post_id):
        try:
            post = Post.objects.get(id=post_id)
            return Tag.objects.filter(name__icontains=name, posts=post)
        except Post.DoesNotExist:
            raise NotFoundError("Post not found")
        except Exception as e:
            raise BaseAPIException(f"Error filtering tags: {e}")


class CreateTag(graphene.Mutation):
    tag = graphene.Field(TagType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        name = graphene.String(required=True)

    def mutate(self, info, name):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            if not name.strip():
                raise BaseAPIException("Tag name is required")

            tag = Tag.objects.create(name=name)
            return CreateTag(tag=tag, message="Tag created successfully", success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error creating tag: {e}")


class UpdateTag(graphene.Mutation):
    tag = graphene.Field(TagType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    def mutate(self, info, id, name):
        try:
            user = get_authenticated_user(info)
            if not user:
                raise AuthenticationError("You are not authenticated")

            try:
                tag = Tag.objects.get(id=id)
            except Tag.DoesNotExist:
                raise NotFoundError("Tag not found")

            if not name.strip():
                raise BaseAPIException("Tag name is required")

            tag.name = name
            tag.save()
            return UpdateTag(tag=tag, message="Tag updated successfully", success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error updating tag: {e}")


class DeleteTag(graphene.Mutation):
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
                tag = Tag.objects.get(id=id)
            except Tag.DoesNotExist:
                raise NotFoundError("Tag not found")

            tag.delete()
            return DeleteTag(message="Tag deleted successfully", success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error deleting tag: {e}")


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
                tag = Tag.objects.get(id=tag_id)
            except (Post.DoesNotExist, Tag.DoesNotExist):
                raise NotFoundError("Post or Tag not found")

            if not (is_superuser(user) or post.user == user):
                raise PermissionDeniedError("You are not allowed to modify this post")

            post.tags.add(tag)
            return AddTagToPost(
                post=post,
                tag=tag,
                message="Tag added to post successfully",
                success=True,
            )

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
                tag = Tag.objects.get(id=tag_id)
            except (Post.DoesNotExist, Tag.DoesNotExist):
                raise NotFoundError("Post or Tag not found")

            if not (is_superuser(user) or post.user == user):
                raise PermissionDeniedError("You are not allowed to modify this post")

            post.tags.remove(tag)
            return RemoveTagFromPost(
                post=post,
                tag=tag,
                message="Tag removed from post successfully",
                success=True,
            )

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"Error removing tag from post: {e}")



class Mutation(graphene.ObjectType):
    create_tag = CreateTag.Field()
    update_tag = UpdateTag.Field()
    delete_tag = DeleteTag.Field()
    add_tag_to_post = AddTagToPost.Field()
    remove_tag_from_post = RemoveTagFromPost.Field()
