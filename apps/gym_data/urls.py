from django.urls import path

from .views import (
    group_exercises_create_view,
    gym_dashboard_view,
    gym_group_create_view,
    gym_report_view,
    gym_session_create_view,
    gym_session_detail_view,
    gym_report_view,
)

app_name = "gym_data"

urlpatterns = [
    path(
        "",
        gym_dashboard_view.gym_dashboard,
        name="dashboard",
    ),

    path(
        "session/create/",
        gym_session_create_view.gym_session_create,
        name="gym_session_create",
    ),

    path(
        "session/<int:session_id>/",
        gym_session_detail_view.gym_session_detail,
        name="gym_session_detail",
    ),

    path(
        "session/<int:session_id>/group/create/",
        gym_group_create_view.gym_group_create,
        name="gym_group_create",
    ),

    path(
        "group/<int:group_id>/exercises/",
        group_exercises_create_view.group_exercises_create,
        name="group_exercises_create",
    ),

    path(
        "reports/",
        gym_report_view.gym_report,
        name="gym_report",
    ),
]