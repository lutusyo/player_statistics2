from django.urls import path
from sheets_generator_app.views import lineup_template, download_lineup_excel

app_name = 'sheets_generator_app'

urlpatterns = [
    path("lineup_sheet/", lineup_template, name="lineup_template"),
    path("download-lineup-excel/", download_lineup_excel, name="download_lineup_excel"),
]
