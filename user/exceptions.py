from rest_framework import status
from rest_framework.exceptions import APIException


from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A bad request occurred."
    default_code = "bad_request"

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail or self.default_detail, code=code or self.default_code)

    def __str__(self):
        if isinstance(self.detail, (list, dict)):
            return str(self.detail)
        return self.detail



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

class PermissionDeniedError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied."
    default_code = "permission_denied"

class NotFoundError(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not found."
    default_code = "not_found"