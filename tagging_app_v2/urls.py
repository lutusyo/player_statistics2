# tagging_app_v2/urls.py
from django.urls import path
from tagging_app_v2 import views
from tagging_app_v2.views import pass_network_enter_data, pass_network_get_data


app_name = 'tagging_app_v2'


urlpatterns = [
    path("match/<int:match_id>/tag_v2/", pass_network_enter_data.create_pass_event_v2, name="tag_panel_v2"),
    # get data
    path("match/<int:match_id>/get_pass_data/", pass_network_get_data.get_pass_data_view, name="pass_data")
]





