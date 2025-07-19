from django.urls import path
from .views import upload_gps_data, gps_dashboard, gps_match_detail

app_name = 'gps_app'

urlpatterns = [
    
    path('upload/', upload_gps_data, name='gps_upload'),
    path('dashboard/', gps_dashboard, name='gps_dashboard'),
    path('match/<int:match_id>/', gps_match_detail, name='gps_match_detail'),

]