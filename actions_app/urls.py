# actions_app/urls.py
from django.urls import path
from . import views

app_name = 'actions_app'

urlpatterns = [
    path('match/<int:match_id>/team_action_stats/', views.match_action_stats, name='match_action_stats'),
]
