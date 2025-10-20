from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = HTMLField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='posts')
    

    def __str__(self):
        return self.title
        
class Tag(models.Model):
    name = models.CharField(max_length=200)
    posts = models.ManyToManyField(Post, related_name='tags')

    def __str__(self):
        return self.name

