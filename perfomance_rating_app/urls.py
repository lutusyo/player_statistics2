from django.urls import path
from perfomance_rating_app.views import match_perfomance_list_view, match_perfomance, season_perfomance



app_name = 'performance_rating_app'

urlpatterns = [

    path('performance-list/<int:team_id>/', match_perfomance_list_view.match_performance_list, name='performance_list'),
    path('match/<int:match_id>/performance/', match_perfomance.match_performance, name='match_performance'),
    path('player/<int:player_id>/season/<str:season>/', season_perfomance.player_season_ratings, name='player_season_ratings'),
    
]





