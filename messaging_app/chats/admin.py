from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message

admin.site.register(Conversation)
admin.site.register(Message)

class CustomUserAdmin(UserAdmin):
    # Remove username from ordering
    ordering = ('email',)  # Order by email instead of username
    
    # Update list display to show relevant fields
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    
    # Update fieldsets to match your custom user model
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role'),
        }),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    # Update add_fieldsets for creating users in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(User, CustomUserAdmin)