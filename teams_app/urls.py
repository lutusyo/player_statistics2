from django.urls import path
from .import views

app_name = 'teams_app'

urlpatterns = [
    path('<str:team>/statistics/', views.team_statistics, name='team_statistics'),
    path('<str:team>/squad/', views.team_squad, name='team_squad'),
    path('<str:team>/table/', views.team_table, name='team_table'),
    path('<str:team>/honour/', views.team_honour, name='team_honour'),
]