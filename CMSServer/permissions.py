from typing import Optional, Union
from django.contrib.auth.models import User
from CMSServer.models import Post, Blog
from .utils import is_superuser, is_blog_owner

def can_view_post(_user, _post) -> bool:
    return True

def can_add_post(user: Optional[User], blog: Blog) -> bool:
    return is_superuser(user) or is_blog_owner(user, blog)

def can_edit_post(user: Optional[User], target: Union[Post, Blog]) -> bool:
    if is_superuser(user):
        return True
    if isinstance(target, Post):
        return is_blog_owner(user, target.blog)
    if isinstance(target, Blog):
        return is_blog_owner(user, target)
    return False

