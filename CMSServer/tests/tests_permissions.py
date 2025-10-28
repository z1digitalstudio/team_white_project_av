from django.test import TestCase
from CMSServer.tests.factories import UserFactory, BlogFactory, PostFactory
from CMSServer.permissions import can_view_post, can_add_post, can_edit_post


class TestPermissions(TestCase):
    def test_can_view_post(self):
        user = UserFactory()
        post = PostFactory(blog=BlogFactory(user=user))
        self.assertTrue(can_view_post(user, post))

    def test_can_add_post(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        self.assertTrue(can_add_post(user, blog))

    def test_can_edit_post(self):
        user = UserFactory()
        post = PostFactory(blog=BlogFactory(user=user))
        self.assertTrue(can_edit_post(user, post))

    def test_can_edit_blog(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        self.assertTrue(can_edit_post(user, blog))

    def test_superuser_can_edit_post(self):
        user = UserFactory(is_superuser=True)
        post = PostFactory(blog=BlogFactory(user=user))
        self.assertTrue(can_edit_post(user, post))

    def test_superuser_can_edit_blog(self):
        user = UserFactory(is_superuser=True)
        blog = BlogFactory(user=user)
        self.assertTrue(can_edit_post(user, blog))

    def test_superuser_can_add_post(self):
        user = UserFactory(is_superuser=True)
        blog = BlogFactory(user=user)
        self.assertTrue(can_add_post(user, blog))

    def test_anonymous_user_can_view_post(self):
        post = PostFactory(blog=BlogFactory(user=UserFactory()))
        self.assertTrue(can_view_post(None, post))

    def test_anonymous_user_can_add_post(self):
        blog = BlogFactory(user=UserFactory())
        self.assertFalse(can_add_post(None, blog))

    def test_anonymous_user_can_edit_post(self):
        post = PostFactory(blog=BlogFactory(user=UserFactory()))
        self.assertFalse(can_edit_post(None, post))

    def test_anonymous_user_can_edit_blog(self):
        blog = BlogFactory(user=UserFactory())
        self.assertFalse(can_edit_post(None, blog))
