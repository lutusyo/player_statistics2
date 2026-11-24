#version1/performance_analysis/urls.py

from django.urls import path
from . import views

app_name = "performance_analysis"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_analysis, name="create_analysis"),
    path("<int:pk>/", views.analysis_detail, name="analysis_detail"),
    path("analysis/<int:pk>/generate/", views.generate_analysis, name="generate_analysis",),

    path(
    "analysis/<int:pk>/export/excel/",
    views.export_excel,
    name="export_excel",
),

path(
    "analysis/<int:pk>/export/pdf/",
    views.export_pdf,
    name="export_pdf",
),

path(
    "analysis/<int:pk>/export/pptx/",
    views.export_pptx,
    name="export_pptx",
),
]
