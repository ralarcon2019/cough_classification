from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
# from users.models import AudioRecording
from django.http import JsonResponse

from django.conf import settings
# User = settings.AUTH_USER_MODEL


from django import forms
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
User = get_user_model()

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
#             recording = AudioRecording.objects.create(
#                 user=request.user, file=audio_file)
#             # Trigger ML task (via Celery or API call)
#             # start_ml_processing.delay(recording.id)  # Example Celery task
#             return JsonResponse({"message": "Audio uploaded successfully!", "file_url": recording.file.url})
#         return JsonResponse({"error": "No file uploaded."}, status=400)
#     return JsonResponse({"error": "Unauthorized or invalid request"}, status=403)
