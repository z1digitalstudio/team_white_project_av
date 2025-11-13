from django.test import TestCase
from blog.tests.factories import BlogFactory, PostFactory
from blog.models import Post

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
        self.assertEqual(str(post), f"{post.title} - {post.blog.title}")
        
class TestBlogModel(TestCase):

    def test_filter_posts_by_blog(self):
        blog1 = BlogFactory()
        blog2 = BlogFactory()
        post1 = PostFactory(blog=blog1)
        post2 = PostFactory(blog=blog2)
        filtered_posts = Post.filter_posts_by_blog(Post.objects.all(), blog1.id)  
        filtered_posts2 = Post.filter_posts_by_blog(Post.objects.all(), blog2.id)
        self.assertEqual(filtered_posts.count(), 1)
        self.assertEqual(filtered_posts[0].id, post1.id)
        self.assertEqual(filtered_posts2.count(), 1)
        self.assertEqual(filtered_posts2[0].id, post2.id)