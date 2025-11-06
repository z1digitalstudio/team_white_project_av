from django.test import TestCase
from blog.tests.factories import UserFactory, BlogFactory, PostFactory
from blog.utils import (
    get_blog_owner,
    is_blog_owner,
    filter_posts_by_blog,
)
from blog.models import Post


class TestBlogUtils(TestCase):
    def test_get_blog_owner(self):
        blog = BlogFactory()
        self.assertIsNotNone(get_blog_owner(blog))

    def test_is_blog_owner(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        self.assertTrue(is_blog_owner(user, blog))

    def test_is_not_blog_owner(self):
        user1 = UserFactory()
        user2 = UserFactory()
        blog = BlogFactory(user=user1)
        self.assertFalse(is_blog_owner(user2, blog))

    def test_filter_posts_by_blog(self):
        blog1 = BlogFactory()
        blog2 = BlogFactory()
        post1 = PostFactory(blog=blog1)
        post2 = PostFactory(blog=blog2)
        filtered_posts = filter_posts_by_blog(Post.objects.all(), blog1.id)
        filtered_posts2 = filter_posts_by_blog(Post.objects.all(), blog2.id)
        self.assertEqual(filtered_posts.count(), 1)
        self.assertEqual(filtered_posts[0].id, post1.id)
        self.assertEqual(filtered_posts2.count(), 1)
        self.assertEqual(filtered_posts2[0].id, post2.id)
