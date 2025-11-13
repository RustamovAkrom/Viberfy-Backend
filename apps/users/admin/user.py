# apps/shared/admin/base.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    GroupAdmin as BaseGroupAdmin,
    UserAdmin as BaseUserAdmin,
)
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

# Получаем текущую модель User (кастомную или стандартную)
User = get_user_model()

# Безопасно снимаем старую регистрацию, если она есть, чтобы не получить AlreadyRegistered / NotRegistered
if Group in admin.site._registry:
    admin.site.unregister(Group)

if User in admin.site._registry:
    admin.site.unregister(User)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_vertical = ("permissions",)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    change_password_form = AdminPasswordChangeForm
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ("id", "email", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("username",)
    list_editable = ("is_active", "is_staff", "is_superuser")
    filter_vertical = ("groups", "user_permissions")
