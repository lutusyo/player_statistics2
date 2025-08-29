from players_app.views  import players_list, player_details, player_matches_details
from django.urls import path

app_name = 'players_app'

urlpatterns = [
    path('players/', players_list.player_list, name='team_statistics'),
    path('players/<int:player_id>/', player_details.player_detail, name='player_detail'),

    # player-match-details, allow 'total' for aggregation
    path('player/<int:player_id>/match/<str:match_id>/', player_matches_details.player_match_detail, name='player_match_detail'),
]
