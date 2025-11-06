from typing import Optional
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)


def is_superuser(user: Optional[User]) -> bool:
    return bool(user and getattr(user, "is_superuser", False))


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = authenticate(username=username, password=password)
    if user and user.is_active:
        return user
    return None


def create_user_token(user: User) -> str:
    token = Token.objects.get_or_create(user=user)[0]
    return token.key


def delete_user_token(user: User) -> bool:
    try:
        user.auth_token.delete()
        return True
    except Token.DoesNotExist:
        return False
    except Exception as e:
        logger.error(f"Error deleting token: {e}")
        return False