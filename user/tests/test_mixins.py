from django.test import TestCase
from unittest.mock import patch
from blog.tests.factories import UserFactory
from user.mixins import AuthenticationMixin
from user.exceptions import InvalidCredentialsError


class TestAuthenticationMixin(TestCase):
    def setUp(self):
        self.mixin = AuthenticationMixin()
        self.user = UserFactory()

    @patch("user.mixins.authenticate_user")
    def test_authenticate_user_success(self, mock_authenticate):
        mock_authenticate.return_value = self.user

        result = self.mixin.authenticate_user("username", "password")

        self.assertEqual(result, self.user)
        mock_authenticate.assert_called_once_with("username", "password")

    @patch("user.mixins.authenticate_user")
    def test_authenticate_user_failure(self, mock_authenticate):
        mock_authenticate.return_value = None

        with self.assertRaises(InvalidCredentialsError):
            self.mixin.authenticate_user("username", "wrong_password")

    @patch("user.mixins.create_user_token")
    def test_create_user_token(self, mock_create_token):
        mock_create_token.return_value = "test_token"

        result = self.mixin.create_user_token(self.user)

        self.assertEqual(result, "test_token")
        mock_create_token.assert_called_once_with(self.user)

    @patch("user.mixins.delete_user_token")
    def test_delete_user_token(self, mock_delete_token):
        mock_delete_token.return_value = True

        result = self.mixin.delete_user_token(self.user)

        self.assertTrue(result)
        mock_delete_token.assert_called_once_with(self.user)

