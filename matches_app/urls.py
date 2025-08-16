from . import views
from django.urls import path
from matches_app.views import  career_stage, fixture_view, get_match_goals, match_detail, player_statistics, result_view, table_view, team_dashboard
from lineup_app.views import lineup_bila_uwanja, substitution, match_lineup_view_with_uwanja

from lineup_app.views.substitution import (
    substitution_panel,
    api_get_lists,
    api_finalize_substitution,
    api_undo_substitution,
)

app_name = 'matches_app'

urlpatterns = [

    # Substitution panel page
    path('matches/<int:match_id>/substitution/', substitution_panel, name='substitution_panel'),

    ## API endpoints for substitution

    # API to get current lists JSON
    path('api/matches/<int:match_id>/substitutions/lists/', api_get_lists, name='api_get_lists'),

    # API to record a substitution (player out & in + minute)
    path('api/matches/<int:match_id>/substitutions/record/', api_finalize_substitution, name='api_finalize_substitution'),

    # API to undo last substitution (optional)
    path('api/matches/<int:match_id>/substitutions/undo/', api_undo_substitution, name='api_undo_substitution'),
    # API to mark match finished
    #path('api/matches/<int:match_id>/finalize/', substitution.api_finalize_substitution, name='api_end_match_and_finalize'),

    # other matches_app URLs 
    
    path('<str:team>/player-statistics/', player_statistics.player_statistics_view, name='players_statistics'),
    path('career-stage/<int:stage_id>/', career_stage.career_stage_detail, name='career_stage_detail'),
    path('dashboard/<int:team_id>/', team_dashboard.team_dashboard_view, name='team_dashboard'),
    path('<str:team>/fixtures/', fixture_view.fixtures_view, name='team_fixtures'),
    path('<str:team>/results/', result_view.results_view, name='team_results'),
    path('<str:code>/table/', table_view.table_view, name='team_table'),
    # Match details
    path('match/<int:match_id>/', match_detail.match_detail, name='match_detail'),

    #path('match/<int:match_id>/add-goal/', views.add_goal, name='add_goal'),
]


