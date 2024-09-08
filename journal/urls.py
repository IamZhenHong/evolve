from django.contrib import admin
from django.urls import path
from . import views
app_name = 'journal'
urlpatterns = [
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('delete/<int:node_id>/', views.delete, name='delete'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('check/',views.check_neo4j_connection, name='check'),
    path('', views.list, name='list'),
]