# game/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # The home page URL remains the same
    path('', views.home_view, name='home'),

    # The URL to process the username also remains the same
    path('start/', views.start_game_view, name='start_game'),

    # CHANGE: The game page URL now accepts a username parameter
    path('game/<str:username>/', views.index, name='game_page'),

    # The analysis URL remains the same (we'll send the username in the request)
    path('analyze/', views.analyze_frame, name='analyze_frame'),
]
