from django.urls import path
from training_app.views.create_session import TrainingSessionCreateView, TrainingSessionListView

urlpatterns = [
    path('new/', TrainingSessionCreateView.as_view(), name='create_training_session'),
    path('list/', TrainingSessionListView.as_view(), name='training_session_list'),
]
