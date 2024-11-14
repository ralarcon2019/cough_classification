from django.urls import path
from . import views

app_name = 'MLContainer'

urlpatterns = [
    path('', views.ML_View, name="detection"),
]
