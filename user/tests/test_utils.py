from django.test import TestCase
from blog.tests.factories import UserFactory
from user.utils import (
    is_superuser,
    authenticate_user,
    create_user_token,
    delete_user_token,
)
from rest_framework.authtoken.models import Token


class TestAuthUtils(TestCase):
    def test_is_superuser(self):
        user = UserFactory(is_superuser=False)
        self.assertFalse(is_superuser(user))

    def test_authenticate_user(self):
        user = UserFactory(password="password")
        authenticated_user = authenticate_user(user.username, "password")
        self.assertEqual(authenticated_user.id, user.id)
        authenticated_user = authenticate_user(user.username, "wrong_password")
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

