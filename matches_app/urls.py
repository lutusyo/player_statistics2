from . import views
from django.urls import path
from .views import match_lineup_view

app_name = 'matches_app'

urlpatterns = [
    path('match/<int:match_id>/lineup/', match_lineup_view, name='match_lineup'),



    path('<str:team>/player-statistics/', views.player_statistics_view, name='players_statistics'),
    path('career-stage/<int:stage_id>/', views.career_stage_detail, name='career_stage_detail'),

    # 
    path('dashboard/<int:team_id>/', views.team_dashboard_view, name='team_dashboard'),


    path('<str:team>/fixtures/', views.fixtures_view, name='team_fixtures'),
    path('<str:team>/results/', views.results_view, name='team_results'),
    path('<str:team>/table/', views.table_view, name='team_table'),

    # Match details
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    #path('match/<int:match_id>/add-goal/', views.add_goal, name='add_goal'),
]