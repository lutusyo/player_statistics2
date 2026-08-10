from django.urls import path
from apps.medical_data.views import *

app_name = "medical_data"

urlpatterns = [
    path("",medical_visit_list,name="medical_visit_list",),
    path("create/",medical_visit_create,name="medical_visit_create",),
    path("<int:pk>/",medical_visit_detail,name="medical_visit_detail",),
    path("<int:pk>/edit/",medical_visit_update,name="medical_visit_update",),
    path("<int:pk>/delete/",medical_visit_delete,name="medical_visit_delete",),
    path("ajax/load-players/",load_players,name="ajax_load_players",), # AJAX URL

    path("<int:visit_id>/attachment/add/",medical_attachment_create,name="medical_attachment_create",),
    path("attachment/<int:pk>/delete/",medical_attachment_delete,name="medical_attachment_delete",),
    path("<int:visit_id>/follow-up/add/",medical_follow_up_create,name="medical_follow_up_create",),
    path("follow-up/<int:pk>/delete/",medical_follow_up_delete,name="medical_follow_up_delete",),
]



