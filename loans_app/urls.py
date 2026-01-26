from django.urls import path
from loans_app import views

app_name = "loans_app"

urlpatterns = [
    path("players/", views.player_list_view, name="player_list"),
    path("players/<int:player_id>/", views.player_detail_view, name="player_detail"),
]
