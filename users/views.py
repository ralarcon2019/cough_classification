import logging
from .models import AudioFile
from django.core.files.base import ContentFile
import base64
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
import uuid
import os
from .ml_model import predict_cough
from .models import AnalysisResult
from django.contrib.auth.mixins import LoginRequiredMixin


from django.contrib.auth import login, logout
# from users.models import AudioFile
from django.http import JsonResponse


from django.conf import settings
# User = settings.AUTH_USER_MODEL


from django import forms
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
User = get_user_model()


# Create your views here.
prob = .88

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("users:dashboard_input")
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
                return redirect("users:dashboard_input")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("main:home")


@method_decorator(csrf_exempt, name="dispatch")
class DashboardInputView(LoginRequiredMixin, View):
    """
    GET:  render the recording + questionnaire form
    POST: decode & save audio, run the CNN, save symptoms & result, redirect to results
    """
    template_name = "dashboard/input.html"

    def get(self, request):
        context = {
            "fever_choices": [
                ("96-99",   "96-99"),
                ("100-101", "100-101"),
                ("101+", "101+"),
            ],
            "sore_throat_choices": [
                ("no",     "No"),
                ("mild",   "Mild"),
                ("severe", "Severe"),
            ],
            "difficulty_breathing_choices": [
                ("no",        "No"),
                ("slight",    "Slight"),
                ("significant", "Significant"),
            ],
            "energy_level_choices": [
                ("normal",   "Normal"),
                ("low",      "Low"),
                ("very_low", "Very Low"),
            ],
            "headache_choices": [
                ("no",   "No"),
                ("mild",      "Mild"),
                ("severe", "Very Low"),
            ],
            "muscle_aches_choices": [
                ("no",   "No"),
                ("mild",      "Mild"),
                ("severe", "Severe"),
            ],
            "nose_choices": [
                ("no",   "No"),
                ("yes",      "Yes"),
            ],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # 1) Decode & save the audio with a unique filename
        audio_data = request.POST.get("audio", "")
        wav_path = None
        if audio_data:
            header, b64 = audio_data.split(",", 1)
            wav_bytes = base64.b64decode(b64)
            filename = f"user_{request.user.id}_{uuid.uuid4().hex}.wav"
            wav_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(wav_path, "wb") as f:
                f.write(wav_bytes)

        # 2) Run the CNN model (if we have audio)
        if wav_path:
            results = predict_cough(wav_path)
        else:
            results = {"healthy": 0.0, "covid": 0.0}

        # 3) Determine label from probabilities
        covid_p = results["covid"]
        if covid_p > prob:
            label = "covid"
        # elif covid_p > 0.2:
        #     label = "symptomatic"
        else:
            label = "healthy"

        # 4) Collect symptom answers
        symptoms = {
            "fever":                request.POST.get("fever"),
            "sore_throat":          request.POST.get("sore_throat"),
            "difficulty_breathing": request.POST.get("difficulty_breathing"),
            "energy_level":         request.POST.get("energy_level"),
            "headache":             request.POST.get("headache"),
            "muscle_aches":         request.POST.get("muscle_aches"),
            "nose":                 request.POST.get("nose"),
        }

        # 5) Persist the result to the database
        AnalysisResult.objects.create(
            user=request.user,
            healthy_prob=results["healthy"],
            covid_prob=results["covid"],
            label=label
        )

        # 6) Store latest in session for summary card
        request.session["cough_results"] = results
        request.session["symptoms"] = symptoms

        return redirect("users:dashboard_results")
    
class DashboardResultsView(View):
    """
    GET: render the results page, showing the latest summary plus a timeline chart
    """
    template_name = "dashboard/results.html"

    def get(self, request):
        # Pull the latest CNN run from session (for the top card)
        results = request.session.pop("cough_results", None)
        symptoms = request.session.pop("symptoms", {})

        if results is None:
            return redirect("users:dashboard_input")

        # Format the summary status
        covid_p = results.get("covid", 0.0)
        status_label = "COVID Likely" if covid_p > prob else "No COVID"
        confidence = round(covid_p * 100, 1)

        # Build the timeline from all past AnalysisResult objects
        history = AnalysisResult.objects.filter(user=request.user)

        timeline_dates = [
            ar.timestamp.strftime("%Y-%m-%d %H:%M")
            for ar in history
        ]
        status_map = {"healthy": 0, "covid": 1}
        timeline_vals = [
            status_map.get(ar.label, 0)
            for ar in history
        ]

        context = {
            "status": {
                "label":      status_label,
                "confidence": confidence,
                "timestamp":  timezone.now(),
            },
            "chart_labels": ['Healthy', 'COVID'],
            "chart_dates":  timeline_dates,
            "chart_vals":   timeline_vals,
            "symptoms":     symptoms,
        }
        return render(request, self.template_name, context)


@login_required
def record_audio(request):
    return render(request, "users/record_audio.html")

logger = logging.getLogger(__name__)





@login_required
@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.user.is_authenticated:
        audio_data = request.POST.get("audio", "")
        if not audio_data:
            return JsonResponse({"error": "No audio data"}, status=400)

        # 1) Decode & save to a unique WAV
        header, b64 = audio_data.split(",", 1)
        wav_bytes = base64.b64decode(b64)
        filename = f"user_{request.user.id}_{uuid.uuid4().hex}.wav"
        save_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(save_path, "wb") as f:
            f.write(wav_bytes)

        # 2) ***RERUN*** your model on this new file
        results = predict_cough(save_path)
        # results == {"healthy": 0.23, "covid": 0.77} (for example)

        # 3) Return the fresh results
        return JsonResponse({
            "message":      "Analysis complete",
            "results":      results,
        })

    return JsonResponse({"error": "Unauthorized"}, status=403)


@login_required
def record_audio(request):
    saved_audio = AudioFile.objects.filter(user=request.user)
    return render(request, "users/record_audio.html", {"saved_audio": saved_audio})
