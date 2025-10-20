from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from .permissions import can_edit_post, can_add_post    


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
        if request.user.is_superuser:
            return qs
        return qs.filter(blog__user=request.user)

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



