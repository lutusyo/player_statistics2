from django.urls import path
from . import views

urlpatterns = [
    path('players/', views.player_list, name='player_list'),
    path('players/<int:player_id>/', views.player_detail, name='player_detail'),
]