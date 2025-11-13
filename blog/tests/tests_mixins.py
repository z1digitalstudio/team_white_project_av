from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.exceptions import PermissionDenied
from unittest.mock import Mock, patch

from blog.mixins import (
    PostReadonlyFieldsMixin,
    PublicReadOnlyMixin,
    BlogOwnerPermissionMixin,
    PostOwnerQuerysetViewSetMixin,
    PostEditorMixin,
)
from blog.tests.factories import UserFactory, BlogFactory, PostFactory
from blog.models import Blog, Post
from django.test import RequestFactory
from blog.exceptions import AuthenticationError


class MockAdmin:
    def get_readonly_fields(self, request, obj=None):
        return []


class MockViewSet:
    def __init__(self, request=None, action="list"):
        self.request = request
        self.action = action

    def get_queryset(self):
        return Post.objects.all()


class PostReadonlyFieldsMixinTest(PostReadonlyFieldsMixin, MockAdmin):
    pass


class TestPostReadonlyFieldsMixin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = PostReadonlyFieldsMixinTest()

    def test_get_readonly_fields_non_superuser(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)

        request = self.factory.get("/")
        request.user = user
        request.user.is_superuser = False

        readonly_fields = self.mixin.get_readonly_fields(request, post)

        self.assertIn("blog", readonly_fields)

    def test_get_readonly_fields_superuser(self):
        user = UserFactory()
        user.is_superuser = True
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)

        request = self.factory.get("/")
        request.user = user

        readonly_fields = self.mixin.get_readonly_fields(request, post)

        self.assertNotIn("blog", readonly_fields)

    def test_get_readonly_fields_no_obj(self):
        user = UserFactory()

        request = self.factory.get("/")
        request.user = user
        request.user.is_superuser = False

        readonly_fields = self.mixin.get_readonly_fields(request, None)

        self.assertNotIn("blog", readonly_fields)


class TestPublicReadOnlyMixin(TestCase):
    def setUp(self):
        self.mixin = PublicReadOnlyMixin()

    def test_get_permissions_list_action(self):
        self.mixin.action = "list"
        permissions = self.mixin.get_permissions()

        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].__class__.__name__, "AllowAny")

    def test_get_permissions_retrieve_action(self):
        self.mixin.action = "retrieve"
        permissions = self.mixin.get_permissions()

        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].__class__.__name__, "AllowAny")

    def test_get_permissions_create_action(self):
        self.mixin.action = "create"
        permissions = self.mixin.get_permissions()

        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].__class__.__name__, "IsAuthenticated")


class TestBlogOwnerPermissionMixin(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.blog = BlogFactory(user=self.user)
        self.other_blog = BlogFactory(user=self.other_user)

    def test_get_permissions_list_action(self):
        mixin = BlogOwnerPermissionMixin()
        mixin.action = "list"
        permissions = mixin.get_permissions()

        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].__class__.__name__, "AllowAny")

    def test_get_permissions_create_action(self):
        mixin = BlogOwnerPermissionMixin()
        mixin.action = "create"
        permissions = mixin.get_permissions()

        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].__class__.__name__, "IsAuthenticated")

    def test_perform_update_owner(self):
        mixin = BlogOwnerPermissionMixin()
        mixin.request = Mock()
        mixin.request.user = self.user

        serializer = Mock()
        serializer.save = Mock()

        mixin.get_object = Mock(return_value=self.blog)
        mixin.perform_update(serializer)

        serializer.save.assert_called_once()

    def test_perform_update_not_owner(self):
        mixin = BlogOwnerPermissionMixin()
        mixin.request = Mock()
        mixin.request.user = self.other_user
        mixin.request.user.is_superuser = False

        serializer = Mock()
        mixin.get_object = Mock(return_value=self.blog)

        with self.assertRaises(PermissionDenied):
            mixin.perform_update(serializer)

    def test_perform_destroy_owner(self):
        mixin = BlogOwnerPermissionMixin()
        mixin.request = Mock()
        mixin.request.user = self.user

        instance = Mock()
        instance.user = self.user
        instance.delete = Mock()

        mixin.perform_destroy(instance)

        instance.delete.assert_called_once()

    def test_perform_destroy_not_owner(self):
        mixin = BlogOwnerPermissionMixin()
        mixin.request = Mock()
        mixin.request.user = self.other_user
        mixin.request.user.is_superuser = False

        instance = Mock()
        instance.user = self.user

        with self.assertRaises(PermissionDenied):
            mixin.perform_destroy(instance)


class TestPostOwnerQuerysetViewSetMixin(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.blog = BlogFactory(user=self.user)
        self.other_blog = BlogFactory(user=self.other_user)
        self.post = PostFactory(blog=self.blog)
        self.other_post = PostFactory(blog=self.other_blog)

    def test_get_queryset_authenticated_user(self):
        class TestViewSet(PostOwnerQuerysetViewSetMixin, MockViewSet):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mixin.request.user = self.user

        mixin.queryset = Post.objects.all()

        queryset = mixin.get_queryset()

        self.assertIn(self.post, queryset)
        self.assertNotIn(self.other_post, queryset)

    def test_get_queryset_superuser(self):
        class TestViewSet(PostOwnerQuerysetViewSetMixin, MockViewSet):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mock_user = Mock()
        mock_user.is_authenticated = True
        mock_user.is_superuser = True
        mixin.request.user = mock_user

        mixin.queryset = Post.objects.all()

        queryset = mixin.get_queryset()

        self.assertIn(self.post, queryset)
        self.assertIn(self.other_post, queryset)

    def test_get_queryset_not_authenticated(self):
        class TestViewSet(PostOwnerQuerysetViewSetMixin, MockViewSet):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mock_user = Mock()
        mock_user.is_authenticated = False
        mixin.request.user = mock_user

        mixin.queryset = Post.objects.all()

        queryset = mixin.get_queryset()

        self.assertIn(self.post, queryset)
        self.assertIn(self.other_post, queryset)

class TestPostEditorMixin(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.blog = BlogFactory(user=self.user)
        self.other_blog = BlogFactory(user=self.other_user)
        self.post = PostFactory(blog=self.blog)

    def test_perform_create_authenticated_user(self):
        class TestViewSet(PostEditorMixin):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mock_user = Mock()
        mock_user.is_authenticated = True
        mock_user.blog = None
        mixin.request.user = mock_user

        serializer = Mock()
        serializer.save = Mock()

        with patch("builtins.hasattr") as mock_hasattr:
            mock_hasattr.return_value = False

            with patch.object(Blog.objects, "create") as mock_create:
                mock_blog = Mock()
                mock_create.return_value = mock_blog

                mixin.perform_create(serializer)

                serializer.save.assert_called_once()
                mock_create.assert_called_once()

    def test_perform_create_not_authenticated(self):
        class TestViewSet(PostEditorMixin):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mixin.request.user = Mock()
        mixin.request.user.is_authenticated = False

        serializer = Mock()

        with self.assertRaises(AuthenticationError):
            mixin.perform_create(serializer)

    @patch("blog.mixins.can_edit_post")
    def test_perform_update_authorized(self, mock_can_edit):
        mock_can_edit.return_value = True

        class TestViewSet(PostEditorMixin):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mixin.request.user = Mock()
        mixin.request.user.is_authenticated = True

        serializer = Mock()
        serializer.save = Mock()

        mixin.get_object = Mock(return_value=self.post)
        mixin.perform_update(serializer)

        serializer.save.assert_called_once()

    @patch("blog.mixins.can_edit_post")
    def test_perform_update_not_authorized(self, mock_can_edit):
        mock_can_edit.return_value = False

        class TestViewSet(PostEditorMixin):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mixin.request.user = Mock()
        mixin.request.user.is_authenticated = True

        serializer = Mock()
        mixin.get_object = Mock(return_value=self.post)

        with self.assertRaises(PermissionDenied):
            mixin.perform_update(serializer)

    @patch("blog.mixins.can_edit_post")
    def test_perform_destroy_authorized(self, mock_can_edit):
        mock_can_edit.return_value = True

        class TestViewSet(PostEditorMixin):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mixin.request.user = Mock()
        mixin.request.user.is_authenticated = True

        instance = Mock()
        instance.delete = Mock()

        mixin.perform_destroy(instance)

        instance.delete.assert_called_once()

    @patch("blog.mixins.can_edit_post")
    def test_perform_destroy_not_authorized(self, mock_can_edit):
        mock_can_edit.return_value = False

        class TestViewSet(PostEditorMixin):
            pass

        mixin = TestViewSet()
        mixin.request = Mock()
        mixin.request.user = Mock()
        mixin.request.user.is_authenticated = True

        instance = Mock()

        with self.assertRaises(PermissionDenied):
            mixin.perform_destroy(instance)
