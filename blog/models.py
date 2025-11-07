from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator


# Create your models here.
class Blog(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="blog")
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(
                5, message="Blog title must be at least 5 characters long"
            ),
            RegexValidator(
                regex=r"^[a-zA-Z0-9\s\-\_áéíóúñÁÉÍÓÚÑ]+$",
                message="Blog title contains invalid characters",
            ),
        ],
        help_text="Blog title (minimum 5 characters)",
        unique=True,
    )
    description = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Post(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(
                5, message="Post title must be at least 5 characters long"
            ),
        ],
        help_text="Post title (minimum 5 characters)",
    )
    content = HTMLField()
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.blog.title}"



    @staticmethod
    def filter_posts_by_blog(queryset, blog_id):
        if blog_id is None:
            return queryset.none()
        try:
            blog_id_int = int(blog_id)
        except ValueError:
            return queryset.none()
        return queryset.filter(blog_id=blog_id_int)


