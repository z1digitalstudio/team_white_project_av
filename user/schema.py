import graphene
from django.contrib.auth.models import User
from django.contrib.auth import logout
from user.utils import (
    authenticate_user,
    create_user_token,
    delete_user_token,
    get_authenticated_user,
)
from user.exceptions import (
    InvalidCredentialsError,
    PermissionDeniedError,
    AuthenticationError,
    BaseAPIException,
    NotFoundError,
)
from Core.graphql_types import UserType
from user.constants import (
    AUTH_NOT_AUTHENTICATED,
    AUTH_INVALID_CREDENTIALS,
    AUTH_LOGIN_SUCCESS,
    AUTH_LOGOUT_SUCCESS,
    USER_ALL_FIELDS_REQUIRED,
    USER_PASSWORDS_DO_NOT_MATCH,
    USER_USERNAME_ALREADY_EXISTS,
    USER_EMAIL_ALREADY_EXISTS,
    USER_PASSWORD_UPDATE_SUCCESS,
    USER_NOT_FOUND,
    USER_DELETE_PERMISSION_DENIED,
    USER_ERROR_RETRIEVING,
    USER_ERROR_RETRIEVING_BY_ID,
    USER_ERROR_CREATING,
    USER_ERROR_DURING_LOGIN,
    USER_ERROR_DURING_LOGOUT,
    USER_ERROR_DELETING,
    USER_ERROR_UPDATING_PASSWORD,
)


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.ID(required=True))

    def resolve_all_users(root, info):
        try:
            return User.objects.all()
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_RETRIEVING}: {e}")

    def resolve_user_by_id(root, info, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise NotFoundError(USER_NOT_FOUND)
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_RETRIEVING_BY_ID}: {e}")


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password_confirm = graphene.String(required=True)

    def mutate(self, info, username, email, password, password_confirm):
        try:
            if not username or not email or not password or not password_confirm:
                raise BaseAPIException(USER_ALL_FIELDS_REQUIRED)

            if password != password_confirm:
                raise BaseAPIException(USER_PASSWORDS_DO_NOT_MATCH)

            if User.objects.filter(username=username).exists():
                raise BaseAPIException(USER_USERNAME_ALREADY_EXISTS)

            if User.objects.filter(email=email).exists():
                raise BaseAPIException(USER_EMAIL_ALREADY_EXISTS)

            user = User.objects.create_user(username=username, email=email, password=password)
            token = create_user_token(user)
            return CreateUser(user=user, token=token)

        except BaseAPIException as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_CREATING}: {e}")


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    message = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        try:
            user = authenticate_user(username, password)
            if not user:
                raise BaseAPIException(AUTH_INVALID_CREDENTIALS)

            token = create_user_token(user)
            return LoginUser(user=user, token=token, message=AUTH_LOGIN_SUCCESS)

        except BaseAPIException as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_DURING_LOGIN}: {e}")


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    def mutate(self, info):
        try:
            user = get_authenticated_user(info)
            if not user or not user.is_authenticated:
                raise BaseAPIException(AUTH_NOT_AUTHENTICATED)

            delete_user_token(user)
            logout(info.context)
            return LogoutUser(success=True, message=AUTH_LOGOUT_SUCCESS, user=user)

        except InvalidCredentialsError as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_DURING_LOGOUT}: {e}")


class DeleteUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_id):
        try:
            current_user = get_authenticated_user(info)
            if not current_user or not current_user.is_authenticated:
                raise BaseAPIException(AUTH_NOT_AUTHENTICATED)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise NotFoundError(USER_NOT_FOUND)

            if user.is_superuser or user.id == current_user.id:
                user.delete()
                return DeleteUser(user=user)
            else:
                raise PermissionDeniedError(USER_DELETE_PERMISSION_DENIED)

        except (AuthenticationError, PermissionDeniedError, InvalidCredentialsError) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_DELETING}: {e}")


class UpdatePassword(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        new_password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    def mutate(self, info, new_password, confirm_password):
        try:
            if new_password != confirm_password:
                raise InvalidCredentialsError(USER_PASSWORDS_DO_NOT_MATCH)

            user = get_authenticated_user(info)
            if not user or not user.is_authenticated:
                raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

            user.set_password(new_password)
            user.save()
            return UpdatePassword(user=user, message=USER_PASSWORD_UPDATE_SUCCESS, success=True)

        except (AuthenticationError, InvalidCredentialsError) as e:
            raise e
        except Exception as e:
            raise BaseAPIException(f"{USER_ERROR_UPDATING_PASSWORD}: {e}")


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    logout_user = LogoutUser.Field()
    delete_user = DeleteUser.Field()
    update_password = UpdatePassword.Field()
