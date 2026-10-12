
from django.urls import path
from apps.individual_data import views

app_name = "individual_training"

urlpatterns = [
    path("", views.session_list, name="session_list"),
    path("create/", views.session_create, name="session_create"),
    path("<int:session_id>/", views.session_detail, name="session_detail"),
    path("<int:session_id>/topics/add/", views.add_session_topic, name="add_session_topic"),
    path("<int:session_id>/participation/add/", views.add_participation, name="add_participation"),
    path("<int:session_id>/participation/<int:participation_id>/interventions/add/", views.add_intervention, name="add_intervention"),
    path("<int:session_id>/evaluation/save/", views.save_evaluation, name="save_evaluation"),
    path("ajax/objectives/", views.objectives_by_topic, name="objectives_by_topic"),

    path("sessions/<int:session_id>/interventions/<int:intervention_id>/coaching-points/add/",views.add_intervention_coaching_point, name="add_intervention_coaching_point",),
    path("weekly-reports/", views.weekly_report, name="weekly_report",),
]
