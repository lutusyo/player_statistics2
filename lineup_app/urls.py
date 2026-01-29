from django.urls import path
from lineup_app.views.lineup_bila_uwanja import  create_lineup_view
from lineup_app.views.match_lineup_view_with_uwanja import pitch_lineup_view
from lineup_app.views import time
from lineup_app.views import lineup_view

from . import views

from lineup_app.views.substitution_panel import (
    api_get_lists,
    api_finalize_substitution,
    api_undo_substitution,
    api_finalize_match,
    substitution_panel,
)

app_name = 'lineup_app'

urlpatterns = [

    path('match/<int:match_id>/lineups/', lineup_view.both_teams_lineup_view, name='both_teams_lineup'),

    path('match/<int:match_id>/team/<int:team_id>/match-lineup', create_lineup_view, name='create_lineup'),
     #path('match/<int:match_id>/match-lineup/', match_lineup_view, name='create_lineup'),

    # lineup
   
    #path('match/<int:match_id>/lineup/', match_lineup_view, name='dashboard_lineup'),
    path("match/<int:match_id>/time/", time.api_match_time, name="api_match_time"),

    # Substitution panel page
    #path('match/<int:match_id>/substitution/', substitution_panel, name='substitution_panel'),
    #path('match/<int:match_id>/match_lineup/', match_lineup_view, name='dashboard_lineup_with_ground'),
    path('match/<int:match_id>/pitch-lineup/', pitch_lineup_view, name='pitch_lineup'),

    # Add these under your substitution panel route
    path('match/<int:match_id>/substitutions/lists/', api_get_lists, name='api_sub_lists'),
    path('match/<int:match_id>/substitutions/record/', api_finalize_substitution, name='api_finalize_substitution'),
    path('match/<int:match_id>/substitutions/undo/', api_undo_substitution, name='api_undo_substitution'),
    path('match/<int:match_id>/finalize/', api_finalize_match, name='api_finalize_match'),



    path('match/<int:match_id>/substitutions/', views.substitution_panel.substitution_panel, name='substitution_panel'),
    path('match/<int:match_id>/record-sub/', views.substitution_panel.substitution_panel, name='record_substitution'),

]




