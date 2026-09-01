from django.urls import path
from version2.psychology_app_v2.views import  player_list, home, upload_excel, player_details, enter_data, assessment_history


app_name = 'psychology_app_v2'


urlpatterns = [
    path('home/', home.home, name='psychology_dashboard'),
    path('upload/', upload_excel.upload_excel, name='upload_excel'),
    path('players/', player_list.player_list, name='player_list'),
    path('player/<int:player_id>/', player_details.player_detail, name='player_detail'),
    path('assessment/add/', enter_data.add_assessment, name='add_assessment'),
    path('assessment/filter-players/', enter_data.filter_players,name='filter_players'),
    path('assessment/history/', assessment_history.assessment_history, name='assessment_history'),
]

