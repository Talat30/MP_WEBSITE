from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('simplex/', views.simplex_view, name='simplex'),
    path('graphical/', views.graphical_view, name='graphical'),
    path('transportation/', views.transportation_view, name='transportation'),
    path('results/<int:problem_id>/', views.results_view, name='results'),
]