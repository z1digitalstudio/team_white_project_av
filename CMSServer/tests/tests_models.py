from django.test import TestCase
from CMSServer.tests.factories import UserFactory, BlogFactory, PostFactory, TagFactory

class TestUserCreation(TestCase):
    def test_user_creation(self):
        user = UserFactory()
        
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.email)
        self.assertFalse(user.is_superuser)

class TestBlogCreation(TestCase):
    def test_blog_creation(self):
        blog = BlogFactory()
        
        self.assertIsNotNone(blog.title)
        self.assertIsNotNone(blog.description)
        self.assertIsNotNone(blog.user)
        self.assertEqual(str(blog), blog.title)

class TestPostCreation(TestCase):
    def test_post_creation(self):
        post = PostFactory()
        
        self.assertIsNotNone(post.title)
        self.assertIsNotNone(post.content)
        self.assertIsNotNone(post.blog)
        self.assertEqual(str(post), post.title)

class TestTagCreation(TestCase):
    def test_tag_creation(self):
        tag = TagFactory()
        
        self.assertIsNotNone(tag.name)
        self.assertEqual(str(tag), tag.name)
        self.assertEqual(tag.posts.count(), 0) 