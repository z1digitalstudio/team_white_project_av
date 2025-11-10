import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from django.contrib.auth import logout
from user.utils import authenticate_user, create_user_token, delete_user_token, get_authenticated_user
from user.exceptions import InvalidCredentialsError, PermissionDeniedError, AuthenticationError

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.ID(required=True))

    def resolve_all_users(root, info):
        return User.objects.all()

    def resolve_user_by_id(root, info, id):
        return User.objects.get(id=id)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password_confirm = graphene.String(required=True)

    def mutate(self, info, username, email, password, password_confirm):
        if password != password_confirm:
            raise InvalidCredentialsError("Passwords do not match")

        if User.objects.filter(username=username).exists():
            raise InvalidCredentialsError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise InvalidCredentialsError("Email already exists")

        if not username or not email or not password or not password_confirm:
            raise InvalidCredentialsError("All fields are required")

        user = User.objects.create_user(username=username, email=email, password=password)
        token = create_user_token(user)
        return CreateUser(user=user, token=token)

class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    message = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = authenticate_user(username, password)
        if not user:
            raise InvalidCredentialsError("Invalid credentials")

        token = create_user_token(user)
        return LoginUser(user=user, token=token, message="Logged in successfully")


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    def mutate(self, info):
        user = get_authenticated_user(info)
        if not user.is_authenticated:
            raise AuthenticationError("You are not authenticated")

        delete_user_token(user)
        logout(info.context)
        return LogoutUser(success=True, message="Logged out successfully", user=user)


class DeleteUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_id):
        user = User.objects.get(id=user_id)
        current_user = info.context.user

        if user.is_superuser or user.id == current_user.id:
            user.delete()
            return DeleteUser(user=user)
        else:
            raise PermissionDeniedError("You are not allowed to delete this user")


class UpdatePassword(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()
    success = graphene.Boolean()
    
    class Arguments:
        new_password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    def mutate(self, info, new_password, confirm_password):
        if new_password != confirm_password:
            raise InvalidCredentialsError("Passwords do not match")

        user = get_authenticated_user(info)
        user.set_password(new_password)
        user.save()
        return UpdatePassword(user=user, message="Password updated successfully", success=True)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    logout_user = LogoutUser.Field()
    delete_user = DeleteUser.Field()
    update_password = UpdatePassword.Field()
