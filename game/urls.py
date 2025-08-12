# game/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # This line correctly points to the 'index' view inside views.py
    path('', views.index, name='index'),

    # This line correctly points to the 'analyze_frame' view inside views.py
    path('analyze/', views.analyze_frame, name='analyze_frame'),
]