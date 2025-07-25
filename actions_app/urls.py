# actions_app/urls.py
from django.urls import path
from . import views

app_name = 'actions_app'

urlpatterns = [
    #path('match/<int:match_id>/team_action_stats/', views.match_action_stats, name='match_action_stats'),
    path('match/<int:match_id>/player/<int:player_id>/actions/', views.player_action_stats, name='player_action_detail'),
    path('match/<int:match_id>/player-actions/', views.player_detailed_action_list, name='player_action_list'),

    path('tagging/<int:match_id>/<str:action_name>/', views.view_action, name='view_action'),

    path('tagging/<int:match_id>/', views.tagging_panel_view, name='tagging_panel'),



]
