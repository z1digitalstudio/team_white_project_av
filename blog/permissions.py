from typing import Optional, Union
from django.contrib.auth.models import User
from blog.models import Post, Blog
from user.utils import is_superuser


def can_view_post(_user, _post) -> bool:
    return True


def can_add_post(user: Optional[User], blog: Blog) -> bool:
    return is_superuser(user) or blog.is_owner(user)


def can_edit_post(user: Optional[User], target: Union[Post, Blog]) -> bool:
    if is_superuser(user):
        return True
    if isinstance(target, Post):
        return target.blog.is_owner(user)
    if isinstance(target, Blog):
        return target.is_owner(user)
    return False
