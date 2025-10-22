from django.test import TestCase
from CMSServer.tests.factories import UserFactory, BlogFactory, PostFactory, TagFactory
from CMSServer.utils import is_superuser, get_blog_owner, is_blog_owner, filter_posts_by_blog, authenticate_user, create_user_token, delete_user_token
from CMSServer.models import Post
from rest_framework.authtoken.models import Token

class TestUtils(TestCase):
    def test_is_superuser(self):
        user = UserFactory(is_superuser=False)
        self.assertFalse(is_superuser(user))

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


    def test_authenticate_user(self):
        user = UserFactory(password='password')
        authenticated_user = authenticate_user(user.username, 'password')
        self.assertEqual(authenticated_user.id, user.id)
        authenticated_user = authenticate_user(user.username, 'wrong_password')
        self.assertIsNone(authenticated_user)

    def test_create_user_token(self):
        user = UserFactory()
        token = create_user_token(user)
        self.assertIsNotNone(token)
        self.assertEqual(token, Token.objects.get(user=user).key)

    def test_delete_user_token(self):
        user = UserFactory() 
        token = create_user_token(user)
        self.assertIsNotNone(token)
        self.assertEqual(token, Token.objects.get(user=user).key)
        self.assertTrue(delete_user_token(user))
        self.assertIsNone(Token.objects.filter(user=user).first())