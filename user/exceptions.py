from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A bad request occurred."
    default_code = "bad_request"

    def __init__(self, detail=None, code=None):
        self.detail = detail if detail is not None else self.default_detail
        self.code = code if code is not None else self.default_code
        super().__init__()


class AuthenticationError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication required."
    default_code = "authentication_required"


class InvalidCredentialsError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid credentials."
    default_code = "invalid_credentials"


class InvalidTokenError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid token."
    default_code = "invalid_token"

