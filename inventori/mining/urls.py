from django.urls import path
from . import views

app_name = 'mining'

urlpatterns = [
    path('run/', views.mining_run, name='mining_run'),
    path('rules/', views.association_rules_list, name='association_rules_list'),
    path('api/rules/', views.association_rules_api, name='association_rules_api'),
    path('dashboard/', views.mining_dashboard, name='mining_dashboard'),
]