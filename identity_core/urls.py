from django.urls import path
from . import views

app_name = 'identity_core'


urlpatterns = [
    path('similar_journal/<int:pk>/', views.similar_journals_view, name='similar_journal'),
    path('similar_journal/<str:identity>/', views.similar_journals_by_identity_view, name='similar_journals_by_identity'),
]