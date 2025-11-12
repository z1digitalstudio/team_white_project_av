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
from tag.constants import (
    AUTH_NOT_AUTHENTICATED,
    TAG_NAME_REQUIRED,
    TAG_CREATED_SUCCESS,
    TAG_UPDATED_SUCCESS,
    TAG_DELETED_SUCCESS,
    TAG_ADDED_TO_POST_SUCCESS,
    TAG_REMOVED_FROM_POST_SUCCESS,
    TAG_NOT_FOUND,
    TAG_POST_OR_TAG_NOT_FOUND,
    TAG_POST_NOT_FOUND,
    TAG_MODIFY_PERMISSION_DENIED,
    TAG_ERROR_FETCHING,
    TAG_ERROR_FILTERING,
    TAG_ERROR_CREATING,
    TAG_ERROR_UPDATING,
    TAG_ERROR_DELETING,
    TAG_ERROR_ADDING_TO_POST,
    TAG_ERROR_REMOVING_FROM_POST,
)


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
            raise BaseAPIException(f"{TAG_ERROR_FETCHING}: {e}")

    def resolve_tag(self, info, id):
        try:
            return Tag.objects.get(id=id)
        except Tag.DoesNotExist:
            raise NotFoundError(TAG_NOT_FOUND)

    def resolve_posts_by_tag(self, info, id):
        try:
            tag = Tag.objects.get(id=id)
            return tag.posts.all()
        except Tag.DoesNotExist:
            raise NotFoundError(TAG_NOT_FOUND)

    def resolve_tags_by_post(self, info, id):
        try:
            post = Post.objects.get(id=id)
            return post.tags.all()
        except Post.DoesNotExist:
            raise NotFoundError(TAG_POST_NOT_FOUND)

    def resolve_tags_by_post_name(self, info, post_name):
        try:
            post = Post.objects.get(name=post_name)
            return post.tags.all()
        except Post.DoesNotExist:
            raise NotFoundError(TAG_POST_NOT_FOUND)

    def resolve_tags_by_name(self, info, name):
        try:
            return Tag.objects.filter(name__icontains=name)
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_FILTERING}: {e}")

    def resolve_tags_by_name_and_post_name(self, info, name, post_name):
        try:
            post = Post.objects.get(name=post_name)
            return Tag.objects.filter(name__icontains=name, posts=post)
        except Post.DoesNotExist:
            raise NotFoundError(TAG_POST_NOT_FOUND)
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_FILTERING}: {e}")

    def resolve_tags_by_name_and_post_id(self, info, name, post_id):
        try:
            post = Post.objects.get(id=post_id)
            return Tag.objects.filter(name__icontains=name, posts=post)
        except Post.DoesNotExist:
            raise NotFoundError(TAG_POST_NOT_FOUND)
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_FILTERING}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            if not name.strip():
                raise BaseAPIException(TAG_NAME_REQUIRED)

            tag = Tag.objects.create(name=name)
            return CreateTag(tag=tag, message=TAG_CREATED_SUCCESS, success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_CREATING}: {e}")


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
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            try:
                tag = Tag.objects.get(id=id)
            except Tag.DoesNotExist:
                raise NotFoundError(TAG_NOT_FOUND)

            if not name.strip():
                raise BaseAPIException(TAG_NAME_REQUIRED)

            tag.name = name
            tag.save()
            return UpdateTag(tag=tag, message=TAG_UPDATED_SUCCESS, success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_UPDATING}: {e}")


class DeleteTag(graphene.Mutation):
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
                tag = Tag.objects.get(id=id)
            except Tag.DoesNotExist:
                raise NotFoundError(TAG_NOT_FOUND)

            tag.delete()
            return DeleteTag(message=TAG_DELETED_SUCCESS, success=True)

        except (AuthenticationError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_DELETING}: {e}")


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
                tag = Tag.objects.get(id=tag_id)
            except (Post.DoesNotExist, Tag.DoesNotExist):
                raise NotFoundError(TAG_POST_OR_TAG_NOT_FOUND)

            if not (is_superuser(user) or post.user == user):
                raise PermissionDeniedError(TAG_MODIFY_PERMISSION_DENIED)

            post.tags.add(tag)
            return AddTagToPost(
                post=post,
                tag=tag,
                message=TAG_ADDED_TO_POST_SUCCESS,
                success=True,
            )

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
                tag = Tag.objects.get(id=tag_id)
            except (Post.DoesNotExist, Tag.DoesNotExist):
                raise NotFoundError(TAG_POST_OR_TAG_NOT_FOUND)

            if not (is_superuser(user) or post.user == user):
                raise PermissionDeniedError(TAG_MODIFY_PERMISSION_DENIED)

            post.tags.remove(tag)
            return RemoveTagFromPost(
                post=post,
                tag=tag,
                message=TAG_REMOVED_FROM_POST_SUCCESS,
                success=True,
            )

        except (AuthenticationError, PermissionDeniedError, BaseAPIException) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{TAG_ERROR_REMOVING_FROM_POST}: {e}")



class Mutation(graphene.ObjectType):
    create_tag = CreateTag.Field()
    update_tag = UpdateTag.Field()
    delete_tag = DeleteTag.Field()
    add_tag_to_post = AddTagToPost.Field()
    remove_tag_from_post = RemoveTagFromPost.Field()
