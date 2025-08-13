# in game/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('start/', views.start_game_view, name='start_game'),
    path('game/<str:username>/', views.index, name='game_page'),
    path('api/analyze_frame/', views.analyze_frame, name='analyze_frame'),
    
    # ADD THIS LINE
    path('api/annotate_only/', views.annotate_only_frame, name='annotate_only'),
]