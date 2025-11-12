from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


class Tag(models.Model):
    posts = models.ManyToManyField("blog.Post", related_name="tags")
    name = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(
                2, message="Tag name must be at least 2 characters long"
            ),
            RegexValidator(
                regex=r"^[a-zA-Z0-9\s\-\_áéíóúñÁÉÍÓÚÑ]+$",
                message="Tag name contains invalid characters",
            ),
        ],
        help_text="Tag name (minimum 2 characters)",
        unique=True,
    )

    def __str__(self):
        return self.name
