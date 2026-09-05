from django.urls import path
from apps.medical_data.views import *
from apps.medical_data.views.medical_coach_views import (medical_coach_dashboard,)
from apps.medical_data.views.medical_dashboard_views import medical_dashboard
from apps.medical_data.views.medical_report_views import medical_report

app_name = "medical_data"

urlpatterns = [

    path("dashboard/",medical_dashboard,name="medical_dashboard",),

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

    path("reports/",medical_report,name="medical_report",),
    path("reports/excel/",medical_report_excel,name="medical_report_excel",),
    path("reports/pdf/",medical_report_pdf,name="medical_report_pdf",),

    path("visit/<int:visit_id>/recovery/create/",recovery_plan_create,name="recovery_plan_create",),
    path("recovery/<int:pk>/", recovery_plan_detail, name="recovery_plan_detail",),
    path("recovery/day/<int:pk>/edit/", recovery_day_update, name="recovery_day_update",),
    path("recovery/day/<int:pk>/complete/",recovery_day_complete, name="recovery_day_complete",),


    path("recovery/<int:pk>/extend/", recovery_plan_extend,name="recovery_plan_extend",),
    path("recovery/<int:pk>/complete/", recovery_plan_complete, name="recovery_plan_complete",),
    path("recovery/<int:pk>/cancel/",recovery_plan_cancel,name="recovery_plan_cancel",),


    #Coach Dashboard
    path("coach/", medical_coach_dashboard, name="medical_coach_dashboard",),


    
]



