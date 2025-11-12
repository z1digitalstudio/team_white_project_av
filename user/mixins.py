from user.utils import authenticate_user, create_user_token, delete_user_token
from user.exceptions import InvalidCredentialsError


class AuthenticationMixin:

    def authenticate_user(self, username: str, password: str):
        user = authenticate_user(username, password)
        if not user:
            raise InvalidCredentialsError("Invalid credentials")
        return user

    def create_user_token(self, user):
        return create_user_token(user)

    def delete_user_token(self, user):
        return delete_user_token(user)

    

