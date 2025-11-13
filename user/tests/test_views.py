from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from blog.tests.factories import UserFactory
from rest_framework.authtoken.models import Token


class TestAuthViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(password="testpass123")

    def test_register(self):
        data = {
            "username": "newuser",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        response = self.client.post("/cms/api/auth/register/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login(self):
        data = {"username": self.user.username, "password": "testpass123"}
        response = self.client.post("/cms/api/auth/login/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_login_invalid_credentials(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/cms/api/auth/login/", data)
        self.assertEqual(response.status_code, 400)

    def test_me(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get("/cms/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)

    def test_logout(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post("/cms/api/auth/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

