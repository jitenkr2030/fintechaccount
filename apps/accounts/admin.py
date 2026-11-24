"""Admin for the accounts app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Customise the admin to use email instead of username."""

    model = User
    ordering = ('-date_joined',)
    list_display = ('email', 'first_name', 'last_name', 'display_role',
                    'is_premium', 'is_email_verified', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_premium', 'is_email_verified',
                   'is_identity_verified', 'roles')
    search_fields = ('email', 'first_name', 'last_name', 'headline', 'city')
    filter_horizontal = ('roles', 'groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone',
                                       'avatar', 'headline', 'bio',
                                       'city', 'state', 'country')}),
        ('Roles', {'fields': ('roles',)}),
        ('Verification', {'fields': ('is_email_verified', 'is_phone_verified',
                                     'is_identity_verified', 'is_premium')}),
        ('Activity', {'fields': ('last_active',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                     'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2', 'roles'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined', 'last_active')
