from django.test import TestCase
from blog.tests.factories import UserFactory
from user.serializers import UserSerializer, RegisterSerializer, LoginSerializer


class TestUserSerializer(TestCase):
    def test_user_serializer(self):
        user = UserFactory()
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data["id"], user.id)
        self.assertEqual(serializer.data["username"], user.username)


class TestRegisterSerializer(TestCase):
    def test_register_serializer_valid(self):
        data = {
            "username": "newuser",
            "password": "password123",
            "password_confirm": "password123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertTrue(user.check_password("password123"))

    def test_register_serializer_passwords_mismatch(self):
        data = {
            "username": "newuser",
            "password": "password123",
            "password_confirm": "different123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class TestLoginSerializer(TestCase):
    def test_login_serializer_valid(self):
        user = UserFactory(password="password123")
        data = {"username": user.username, "password": "password123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_login_serializer_invalid_credentials(self):
        user = UserFactory(password="password123")
        data = {"username": user.username, "password": "wrongpassword"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_login_serializer_missing_fields(self):
        data = {"username": "testuser"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())

