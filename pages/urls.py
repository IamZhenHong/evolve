from django.urls import path
from . import views

app_name = 'pages'
urlpatterns = [
    path('home/', views.home, name='home'),
]