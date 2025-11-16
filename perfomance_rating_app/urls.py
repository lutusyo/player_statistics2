from django.urls import path
from perfomance_rating_app.views import ( match_perfomance_list_view,
                                         match_perfomance,
                                         season_perfomance,
                                          staffRating )



app_name = 'performance_rating_app'

urlpatterns = [

    path('performance-list/<int:team_id>/', match_perfomance_list_view.match_performance_list, name='performance_list'),
    path('match/<int:match_id>/performance/', match_perfomance.match_performance, name='match_performance'),
    path("season/<str:season>/overview/", season_perfomance.season_player_overview, name="season_player_overview"),

    #path("matches/<int:match_id>/rate/", staffRating.staff_rate_players_view, name="staff-rate-players"),


    path("send-links/<int:match_id>/", staffRating.send_rating_links, name="send_rating_links"),
    path("rate/<uuid:token_uuid>/", staffRating.staff_rate_with_token, name="staff_rate_with_token"),

    path("match/<int:match_id>/aggregates/", staffRating.match_staff_aggregates, name="match_staff_aggregates"),


]


