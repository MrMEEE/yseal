"""
Admin dashboard URL configuration.
"""
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('policies/', views.policies_list, name='policies_list'),
    path('contributors/', views.contributors_list, name='contributors_list'),
    path('users/', views.users_list, name='users_list'),
    path('tags/', views.tags_list, name='tags_list'),
    path('ratings/', views.ratings_list, name='ratings_list'),
]
