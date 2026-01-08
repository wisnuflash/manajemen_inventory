from django.urls import path
from . import views

app_name = 'mining'

urlpatterns = [
    path('', views.mining_index, name='mining_index'),
    path('api/rules/', views.association_rules_api, name='association_rules_api'),
    # Redirect old URLs to the new consolidated view
    path('run/', views.mining_index, name='mining_run'),
    path('rules/', views.mining_index, name='association_rules_list'),
    path('dashboard/', views.mining_index, name='mining_dashboard'),
]