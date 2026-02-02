from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()   

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'username', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)

