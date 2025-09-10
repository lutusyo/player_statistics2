from django.urls import path
from . import views

app_name = 'teams_app'

urlpatterns = [
    path('<int:pk>/statistics/', views.team_statistics, name='team_statistics'),
    path('<int:pk>/table/', views.team_table, name='team_table'),
    path('<int:pk>/honour/', views.team_honour, name='team_honour'),

    # Squad view
    path('squad/<int:pk>/', views.team_squad_view, name='team_squad'),

    # Staff list
    path('staff/', views.staff_list, name='staff_list'),
]
