from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserProfile, Cookie

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'idrole', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'idrole')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('username', 'idrole', 'idpart')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'idrole', 'idpart'),
        }),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('role',)
    readonly_fields = ('slug',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'country')
    search_fields = ('user__email', 'user__username', 'phone_number')

@admin.register(Cookie)
class CookieAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_given', 'consent_date')
    list_filter = ('consent_given',)
    search_fields = ('user__email', 'user__username')