from django.test import TestCase
from CMSServer.mixins import PostReadonlyFieldsMixin, PostEditorMixin
from CMSServer.tests.factories import UserFactory, BlogFactory, PostFactory
from django.test import RequestFactory

class MockAdmin:
    def get_readonly_fields(self, request, obj=None):
        return []

class PostReadonlyFieldsMixinTest(PostReadonlyFieldsMixin, MockAdmin):
    pass

class TestPostReadonlyFieldsMixin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = PostReadonlyFieldsMixinTest()
        
    def test_get_readonly_fields(self):
        user = UserFactory()
        blog = BlogFactory(user=user)
        post = PostFactory(blog=blog)
        
        request = self.factory.get('/')
        request.user = user
        
        readonly_fields = self.mixin.get_readonly_fields(request, post)
        
        self.assertIn('blog', readonly_fields)