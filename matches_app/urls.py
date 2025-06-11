from . import views
from django.urls import path

app_name = 'matches_app'

urlpatterns = [
    path('player-statistics/', views.player_statistics_view, name='players_statistics'),
    path('career-stage/<int:stage_id>/', views.career_stage_detail, name='career_stage_detail'),
]