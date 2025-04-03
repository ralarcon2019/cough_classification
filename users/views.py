import logging
from .models import AudioFile
from django.core.files.base import ContentFile
import base64
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.contrib.auth import login, logout
# from users.models import AudioFile
from django.http import JsonResponse


from django.conf import settings
# User = settings.AUTH_USER_MODEL


from django import forms
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
User = get_user_model()

logger = logging.getLogger(__name__)

# Create your views here.


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("main:home")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("main:home")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("main:home")


# # user/views.py
# @csrf_exempt
# def upload_audio(request):
#     if request.method == "POST" and request.user.is_authenticated:
#         audio_file = request.FILES.get('audio_file')
#         if audio_file:
#             recording = AudioFile.objects.create(
#                 user=request.user, file=audio_file)
#             # Trigger ML task (via Celery or API call)
#             # start_ml_processing.delay(recording.id)  # Example Celery task
#             return JsonResponse({"message": "Audio uploaded successfully!", "file_url": recording.file.url})
#         return JsonResponse({"error": "No file uploaded."}, status=400)
#     return JsonResponse({"error": "Unauthorized or invalid request"}, status=403)

@login_required
def record_audio(request):
    return render(request, "users/record_audio.html")


# @login_required
# def upload_audio(request):
#     if request.method == "POST" and request.FILES.get("audio"):
#         audio = AudioFile.objects.create(
#             user=request.user,
#             file=request.FILES["audio"]
#         )
#         return JsonResponse({
#             "message": "Audio uploaded successfully!",
#             "file_url": audio.file.url
#         })
#     return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def upload_audio(request):
    if request.method == "POST":
        # Option 1: Check if a file was uploaded (e.g. via FormData with Blob)
        if request.FILES.get("audio"):
            audio = AudioFile.objects.create(
                user=request.user,
                file=request.FILES["audio"]
            )
            return JsonResponse({
                "message": "Audio uploaded successfully!",
                "file_url": audio.file.url
            })

        # Option 2: Check for a base64-encoded audio string in POST data
        audio_data = request.POST.get("audio")
        if audio_data:
            try:
                # Expected format: "data:audio/wav;base64,AAAA..."
                header, encoded = audio_data.split(',', 1)
                # You can add additional checks on header if needed
                audio_content = base64.b64decode(encoded)
                # Create a ContentFile, giving it a filename
                audio_file = ContentFile(audio_content, name="recording.wav")
                logger.debug("Using storage: %s", DEFAULT_FILE_STORAGE)

                audio = AudioFile.objects.create(
                    user=request.user,
                    file=audio_file
                )
                return JsonResponse({
                    "message": "Audio uploaded successfully!",
                    "file_url": audio.file.url
                })
            except Exception as e:
                return JsonResponse({"error": "Failed to decode audio data: " + str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def record_audio(request):
    saved_audio = AudioFile.objects.filter(user=request.user)
    return render(request, "users/record_audio.html", {"saved_audio": saved_audio})
