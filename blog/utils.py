from typing import Optional
from django.contrib.auth.models import User
from blog.models import Blog


def get_blog_owner(blog: Blog) -> Optional[User]:
    return getattr(blog, "user", None)


def is_blog_owner(user: Optional[User], blog: Blog) -> bool:
    return bool(user and user == get_blog_owner(blog))


def filter_posts_by_blog(queryset, blog_id):
    if blog_id:
        try:
            blog_id = int(blog_id)
            return queryset.filter(blog_id=blog_id)
        except (ValueError, TypeError):
            return queryset
    return queryset
