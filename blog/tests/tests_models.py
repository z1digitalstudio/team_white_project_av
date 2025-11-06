from django.test import TestCase
from blog.tests.factories import UserFactory, BlogFactory, PostFactory

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