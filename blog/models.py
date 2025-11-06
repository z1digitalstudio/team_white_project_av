from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator


# Create your models here.
class Blog(models.Model):
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
    )
    description = HTMLField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Post(models.Model):
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
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="posts")

    def __str__(self):
        return self.title


