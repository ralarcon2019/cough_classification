from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings



class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):  # ,email
        if not username:
            raise ValueError("Must have a username")
        # email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)  # , email=email
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields): # ,email
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)  # , email
        

class Users(AbstractUser):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL,
    #                          on_delete=models.CASCADE, null=True)  # ✅ Correct
    # email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    birthday = models.DateTimeField(null=True)
    gender = models.CharField(null=True,
        max_length=6,
        choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE')]
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username







# # from django.contrib.auth.models import User
# def user_audio_upload_path(instance, filename):
#     # Example: 'user_1/audio/recording_20231130.wav'
#     return f'user_{instance.user.id}/audio/{filename}'

# class AudioRecording(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     file = models.FileField(upload_to=user_audio_upload_path)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Audio by {self.user.username} at {self.uploaded_at}"