from django.urls import path
from lineup_app.views.lineup_bila_uwanja import match_lineup_view
from lineup_app.views.match_lineup_view_with_uwanja import pitch_lineup_view
from lineup_app.views.substitution import substitution_panel
from lineup_app.views import time



app_name = 'lineup_app'

urlpatterns = [

       # lineup
    path('match/<int:match_id>/match-lineup/', match_lineup_view, name='create_lineup'),

    path('match/<int:match_id>/lineup/', match_lineup_view, name='dashboard_lineup'),

    
    path("match/<int:match_id>/time/", time.api_match_time, name="api_match_time"),



    # Substitution panel page
    path('match/<int:match_id>/substitution/', substitution_panel, name='substitution_panel'),


    #path('match/<int:match_id>/match_lineup/', match_lineup_view, name='dashboard_lineup_with_ground'),

    path('match/<int:match_id>/pitch-lineup/', pitch_lineup_view, name='pitch_lineup'),
]