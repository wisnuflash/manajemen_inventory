from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Purchase Order URLs
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:po_id>/add-item/', views.purchase_order_add_item, name='purchase_order_add_item'),
    path('purchase-orders/<int:pk>/submit/', views.purchase_order_submit, name='purchase_order_submit'),
    path('purchase-orders/<int:po_id>/receive/', views.receive_purchase_order, name='receive_purchase_order'),
    path('purchase-orders/remove-item/<int:item_id>/', views.remove_po_item, name='remove_po_item'),
    
    # Goods Receipt URLs
    path('goods-receipts/', views.goods_receipt_list, name='goods_receipt_list'),
    path('goods-receipts/create/', views.goods_receipt_create, name='goods_receipt_create'),
    path('goods-receipts/<int:pk>/', views.goods_receipt_detail, name='goods_receipt_detail'),
]