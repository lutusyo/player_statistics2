from . import views
from django.urls import path

app_name = 'players_app'

urlpatterns = [
    path('players/', views.player_list, name='team_statistics'),
    path('players/<int:player_id>/', views.player_detail, name='player_detail'),

    # player-match-details, allow 'total' for aggregation
    path('player/<int:player_id>/match/<str:match_id>/', views.player_match_detail, name='player_match_detail'),
]
