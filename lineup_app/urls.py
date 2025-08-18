from django.urls import path
from lineup_app.views.lineup_bila_uwanja import match_lineup_view_during_match
from lineup_app.views.match_lineup_view_with_uwanja import match_lineup_view
from lineup_app.views.substitution import substitution_panel



app_name = 'lineup_app'

urlpatterns = [

       # lineup
    path('match/<int:match_id>/match-lineup/', match_lineup_view, name='create_lineup'),
    path('match/<int:match_id>/lineup/', match_lineup_view_during_match, name='dashboard_lineup'),

    # Substitution panel page
    path('match/<int:match_id>/substitution/', substitution_panel, name='substitution_panel'),


    #path('match/<int:match_id>/match_lineup/', match_lineup_view, name='dashboard_lineup_with_ground'),


]