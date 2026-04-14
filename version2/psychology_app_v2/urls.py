from django.urls import path
from version2.psychology_app_v2.views import  player_list, home, upload_excel, player_details

urlpatterns = [
    path('home/', home.home, name='psychology_dashboard'),
    path('upload/', upload_excel.upload_excel, name='upload_excel'),
    path('players/', player_list.player_list, name='player_list'),
    path('player/<int:player_id>/', player_details.player_detail, name='player_detail'),
]

