from django.urls import path
from .views import upload_gps_data, gps_match_list, gps_match_detail, gps_match_detail_positions

app_name = 'gps_app'

urlpatterns = [
    path('upload/', upload_gps_data.upload_gps_data, name='gps_upload'),
    path('dashboard/', gps_match_list.gps_matches_list, name='gps_dashboard'),
    path('match/<int:match_id>/gps_data/', gps_match_detail.gps_match_detail, name='gps_data'),

     # ... gps data according to position
    path('match/<int:match_id>/position_detail/', gps_match_detail_positions.gps_position_detail, name='gps_position_detail'),
]