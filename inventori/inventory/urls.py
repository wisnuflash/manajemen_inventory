from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Warehouse URLs
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/update/', views.warehouse_update, name='warehouse_update'),
    path('warehouses/<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
    
    # Stock URLs
    path('stocks/', views.stock_list, name='stock_list'),
    path('stocks/adjustment/', views.stock_adjustment, name='stock_adjustment'),
    
    # Stock Movement URLs
    path('movements/', views.stock_movement_list, name='stock_movement_list'),
    
    # Reorder Policy URLs
    path('reorder-policies/', views.reorder_policy_list, name='reorder_policy_list'),
    path('reorder-policies/create/', views.reorder_policy_create, name='reorder_policy_create'),
    path('reorder-policies/<int:pk>/update/', views.reorder_policy_update, name='reorder_policy_update'),
    
    # Alerts
    path('low-stocks/', views.low_stock_alerts, name='low_stock_alerts'),
]