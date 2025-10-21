from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from .permissions import can_edit_post, can_add_post
from .utils import filter_posts_by_blog, authenticate_user, create_user_token, delete_user_token


class PostReadonlyFieldsMixin:
    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser and obj is not None and 'blog' not in ro:
            ro.append('blog')
        return ro

class LimitBlogChoicesToOwnerMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'blog' and not request.user.is_superuser:
            if formfield is not None and hasattr(formfield, 'queryset'):
                formfield.queryset = formfield.queryset.filter(user=request.user)
        return formfield

class PostOwnerQuerysetAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_authenticated:
            return qs.none()
        if not request.user.is_superuser:
            return qs.filter(blog__user=request.user)
        return qs

class PostOwnerQuerysetViewSetMixin:

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs
        if not self.request.user.is_superuser:
            return qs.filter(blog__user=self.request.user)
        return qs

class PostEditorMixin:
    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            return super().save_model(request, obj, form, change)

        if not change:
            if not can_add_post(request.user, obj.blog):
                raise PermissionDenied(_("You are not allowed to add this post."))
        else:
            if 'blog' in getattr(form, 'changed_data', []):
                if not can_edit_post(request.user, obj.blog):
                    raise PermissionDenied(_("You are not allowed to move the post to a blog that is not yours."))

        return super().save_model(request, obj, form, change)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied(_("Authentication required to create posts."))
        
        if not hasattr(self.request.user, 'blog'):
            from .models import Blog
            blog = Blog.objects.create(
                title=f"Blog de {self.request.user.username}",
                description="Blog personal",
                user=self.request.user
            )
            serializer.save(blog=blog)
        else:
            serializer.save(blog=self.request.user.blog)

    def perform_update(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied(_("Authentication required to edit posts."))
        
        if not can_edit_post(self.request.user, self.get_object()):
            raise PermissionDenied(_("You are not allowed to edit this post."))
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_authenticated:
            raise PermissionDenied(_("Authentication required to delete posts."))
        
        if not can_edit_post(self.request.user, instance):
            raise PermissionDenied(_("You are not allowed to delete this post."))
        instance.delete()

class FilterPostsByBlogViewSetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        blog_id = self.request.query_params.get('blog_id')
        return filter_posts_by_blog(qs, blog_id)

class AuthenticationMixin:
    
    def authenticate_user(self, username: str, password: str):
        user = authenticate_user(username, password)
        if not user:
            raise PermissionDenied("Invalid credentials")
        return user
    
    def create_user_token(self, user):
        return create_user_token(user)
    
    def delete_user_token(self, user):
        return delete_user_token(user)