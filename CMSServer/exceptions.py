from rest_framework import exceptions, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

class BaseAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ('A bad request occurred.')
    default_code = 'bad_request'

    def __init__(self, detail=None, code=None):
        self.detail = detail if detail is not None else self.default_detail
        self.code = code if code is not None else self.default_code
        super().__init__()

class AuthenticationError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ('Authentication required.')
    default_code = 'authentication_required'

class InvalidCredentialsError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ('Invalid credentials.')
    default_code = 'invalid_credentials'

class InvalidTokenError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ('Invalid token.')
    default_code = 'invalid_token'

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, BaseAPIException):
        if exc.status_code >= 500:
            logger.error(f"{exc.__class__.__name__}: {exc.detail}")
        
        return Response(
            {
                'error': _get_error_type(exc.status_code),
                'message': str(exc.detail),
                'code': exc.code
            },
            status=exc.status_code
        )
    
    if response is not None:
        if hasattr(exc, 'status_code'):
            status_code = exc.status_code
        elif hasattr(response, 'status_code'):
            status_code = response.status_code
        else:
            status_code = 400
        
        if hasattr(exc, 'code'):
            error_code = exc.code
        else:
            error_code = 'api_error'
        
        detail = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
        
        return Response(
            {
                'error': _get_error_type(status_code),
                'message': detail,
                'code': error_code
            },
            status=status_code
        )
    
    if response is None:
        logger.error(f"Unhandled exception: {type(exc).__name__}", exc_info=True)
        return Response(
            {'error': 'Internal Server Error', 'message': 'An unexpected error occurred.', 'code': 'internal_server_error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response

def _get_error_type(status_code):
    if status_code == 400:
        return 'Bad Request'
    elif status_code == 401:
        return 'Unauthorized'
    elif status_code == 403:
        return 'Forbidden'
    elif status_code == 404:
        return 'Not Found'
    elif status_code >= 500:
        return 'Internal Server Error'
    else:
        return 'Error'