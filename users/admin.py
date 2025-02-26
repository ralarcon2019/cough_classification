

# # Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# from .forms import CustomUserCreationForm, CustomUserChangeForm
# from .models import Users

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = User  # Use your custom user model
    list_display = ("username", "first_name", "last_name", "email", "birthday", "gender",
                    "is_staff", "is_active")  # Show custom fields in the user list
    list_filter = ("is_staff", "is_superuser", "is_active",
                   "gender")  # Add filters for easy navigation
    fieldsets = (
        # Default user fields
        (None, {"fields": ("username", "first_name",
         "last_name", "email", "password")}),
        # Custom fields section
        ("Personal Info", {"fields": ("birthday", "gender")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser",
         "groups", "user_permissions")}),  # Standard permissions
        # Standard timestamps
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (  # Fields used when adding a new user in admin
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email",  "first_name", "last_name", "birthday", "gender", "password", "is_staff", "is_active"),
        }),
    )
    # Enable searching by username, email, or phone
    search_fields = ("username", "email")
    ordering = ("username",)  # Default srting order


admin.site.register(User, CustomUserAdmin)  # Register the custom admin panel
