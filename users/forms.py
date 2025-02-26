# # users/forms.py
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth import get_user_model
# from .models import Users

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "first_name",
                  "last_name", "birthday", "gender")  # 'password'
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.birthday = self.cleaned_data["birthday"]
        user.gender = self.cleaned_data["gender"]
        
        
        if commit:
            user.save()
        return user
        

# class CustomUserCreationForm(UserCreationForm):

#     class Meta:
#         model = CustomUser
#         fields = ("username", "email")


# class CustomUserChangeForm(UserChangeForm):

#     class Meta:
#         model = CustomUser
#         fields = ("username", "email")
