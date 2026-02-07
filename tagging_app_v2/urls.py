# tagging_app_v2/urls.py
from django.urls import path
from tagging_app_v2 import views
from tagging_app_v2.views import pass_network, pass_network_enter_data


app_name = 'tagging_app_v2'


urlpatterns = [
    path("match/<int:match_id>/tag_v2/", pass_network_enter_data.create_pass_event_v2, name="tag_panel_v2"),
    path("match/<int:match_id>/pass-events/", pass_network.pass_network_dashboard, name="pass_events_v2_list"),
    
]





