import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from CMSServer.models import Blog, Post, Tag


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "defaultpassword123"
        self.set_password(password)
        if create:
            self.save()


class BlogFactory(DjangoModelFactory):
    class Meta:
        model = Blog

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text", max_nb_chars=200)
    user = factory.SubFactory(UserFactory)


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("text", max_nb_chars=500)
    blog = factory.SubFactory(BlogFactory)


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")

    @factory.post_generation
    def posts(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for post in extracted:
                self.posts.add(post)
