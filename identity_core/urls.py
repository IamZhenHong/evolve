from django.urls import path
from . import views

app_name = 'identity_core'


urlpatterns = [
    path('graph/', views.show_graph, name='dashboard'),  
    path('get_graph/', views.get_graph, name='get_graph'),
    path('graph_view/', views.graph_view, name='graph_view'),
    path('graph_data/', views.graph_data, name='graph_data'),
]