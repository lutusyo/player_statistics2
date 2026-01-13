from django.urls import path
from players_app.api_views.player_details_api_views import PlayerDetailAPIView


urlpatterns = [
    path('players/<int:player_id>/', PlayerDetailAPIView.as_view()),
]






