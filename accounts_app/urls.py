from django.urls import path
from django.contrib.auth import views as auth_views
from accounts_app.forms import CustomLoginForm
from . import views
from django.urls import path
from .views import data_analyst_responsibilities

app_name = 'accounts_app'

urlpatterns = [
    
    # My responsibilities
    path("secret-data-analyst-tasks-2025/", data_analyst_responsibilities, name="data_analyst_responsibilities"),
    
    path('', views.index, name='home'),

    path('signup/', views.signup_view, name='signup'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts_app/login.html',authentication_form=CustomLoginForm), name='login'),

    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts_app/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts_app/password_change_done.html'), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts_app/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts_app/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts_app/password_reset_complete.html'), name='password_reset_complete'),
]
