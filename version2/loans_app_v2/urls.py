from django.urls import path
from version2.loans_app_v2 import views

app_name = "loans_app_v2"

urlpatterns = [
    path("players/", views.loan_players_list_view, name="loan_players_list"),
    path("players/<int:player_id>/", views.loan_player_detail_view, name="loan_player_detail"),
 ]
