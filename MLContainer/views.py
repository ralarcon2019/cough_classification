from django.shortcuts import render

# Create your views here.

def ML_View(request):
    return render(request, "MLContainer/main.html")
