from django.contrib import admin
from django.urls import path
from .views import create, update, delete, detail, list
urlpatterns = [
    path('create/', create, name='create'),
    path('update/<int:pk>/', update, name='update'),
    path('delete/<int:pk>/', delete, name='delete'),
    path('detail/<int:pk>/', detail, name='detail'),
    path('', list, name='list'),
]