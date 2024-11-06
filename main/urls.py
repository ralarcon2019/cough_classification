from django.urls import path, re_path
from . import views
from django.views.static import serve
from django.conf import settings

app_name = 'main'
urlpatterns = [
   
    path('', views.home, name='home'),
    path('project/', views.project, name='project'),
]
