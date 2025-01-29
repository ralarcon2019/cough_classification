from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Create your models here.


# from django.contrib.auth.models import User

def user_audio_upload_path(instance, filename):
    # Example: 'user_1/audio/recording_20231130.wav'
    return f'user_{instance.user.id}/audio/{filename}'




# users/models.py

# from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username



class AudioRecording(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_audio_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audio by {self.user.username} at {self.uploaded_at}"