from django.urls import path
from .views import upload_gps_data, gps_dashboard

app_name = 'gps_app'

urlpatterns = [
    
    path('upload/', upload_gps_data, name='gps_upload'),
    path('dashboard/', gps_dashboard, name='gps_dashboard'),

]