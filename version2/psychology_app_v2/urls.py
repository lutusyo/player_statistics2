from django.urls import path
from .views import upload_excel
from .views import player_list, home, player_detail

urlpatterns = [
    path('home/', home, name='psychology_dashboard'),
    path('upload/', upload_excel, name='upload_excel'),
    path('players/', player_list, name='player_list'),
    path('player/<int:player_id>/', player_detail, name='player_detail'),
]

