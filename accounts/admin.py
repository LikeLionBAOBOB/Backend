from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *
from .forms import AdminUserCreationForm

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = AdminUserCreationForm

    list_display = ("nickname", "email", "phone", "role", "is_staff", "is_superuser")
    search_fields = ("nickname", "email", "phone")

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("role", "nickname", "email", "phone", "password1", "password2"),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)