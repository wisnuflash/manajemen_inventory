from django.urls import path
from . import views

app_name = 'summary'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/top-products/', views.api_top_products, name='api_top_products'),
    path('api/top-rules/', views.api_top_rules, name='api_top_rules'),
]