from django.urls import path
from . import views

app_name = 'announcements_app'

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('<str:age_group>/', views.announcement_by_age_group, name='announcement_by_group'),
]
