from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # POS (Point of Sale) URLs
    path('pos/', views.pos_view, name='pos'),
    path('pos/<int:sale_id>/add-item/', views.pos_add_item, name='pos_add_item'),
    path('pos/<int:sale_id>/complete/', views.pos_complete_sale, name='pos_complete'),
    path('pos/<int:sale_id>/cancel/', views.pos_cancel_sale, name='pos_cancel'),
    path('pos/remove-item/<int:item_id>/', views.remove_sale_item, name='remove_sale_item'),
    
    # AJAX endpoint for searching products
    path('ajax/search-product/', views.search_product_ajax, name='search_product_ajax'),
    
    # Sales management URLs
    path('', views.sale_list, name='sale_list'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
]