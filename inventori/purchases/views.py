from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import PurchaseOrder, POItem, GoodsReceipt
from .forms import PurchaseOrderForm, POItemForm, GoodsReceiptForm
from master.models import Product
from inventory.models import Stock, StockMove
from inventory.services import update_stock


@login_required
def purchase_order_list(request):
    # Check if user has permission to access purchase orders
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    purchase_orders = PurchaseOrder.objects.all().order_by('-ordered_at')
    return render(request, 'purchases/purchase_order_list.html', {'purchase_orders': purchase_orders})


@login_required
def purchase_order_create(request):
    # Check if user has permission to create purchase orders
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save()
            messages.success(request, f'Purchase Order {po.po_number} berhasil dibuat')
            return redirect('purchases:purchase_order_detail', pk=po.id)
    else:
        # Generate new PO number
        latest_po = PurchaseOrder.objects.order_by('-id').first()
        next_number = 1 if not latest_po else latest_po.id + 1
        po_number = f"PO-{next_number:06d}"
        form = PurchaseOrderForm(initial={'po_number': po_number})
    
    return render(request, 'purchases/purchase_order_form.html', {'form': form})


@login_required
def purchase_order_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    po_items = POItem.objects.filter(purchase_order=po).select_related('product')
    total_amount = sum(item.get_total() for item in po_items)
    
    # Update PO total amount
    if po.total_amount != total_amount:
        po.total_amount = total_amount
        po.save()
    
    return render(request, 'purchases/purchase_order_detail.html', {
        'po': po,
        'po_items': po_items,
        'total_amount': total_amount
    })


@login_required
def purchase_order_add_item(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)
    
    if request.method == 'POST':
        form = POItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            
            # Get product by SKU
            product_sku = request.POST.get('product_sku')
            try:
                product = Product.objects.get(sku=product_sku, is_active=True)
            except Product.DoesNotExist:
                messages.error(request, f'Produk dengan SKU {product_sku} tidak ditemukan')
                return redirect('purchases:purchase_order_add_item', po_id=po_id)
            
            # Set the product
            item.product = product
            item.purchase_order = po
            item.save()
            
            messages.success(request, f'{item.qty} {product.name} ditambahkan ke PO')
            return redirect('purchases:purchase_order_add_item', po_id=po_id)
    else:
        form = POItemForm()
    
    # Get current items in the PO
    po_items = POItem.objects.filter(purchase_order=po).select_related('product')
    total_amount = sum(item.get_total() for item in po_items)
    
    context = {
        'po': po,
        'form': form,
        'po_items': po_items,
        'total_amount': total_amount,
    }
    return render(request, 'purchases/purchase_order_add_item.html', context)


@login_required
def remove_po_item(request, item_id):
    """
    Remove an item from the purchase order
    """
    item = get_object_or_404(POItem, id=item_id)
    po_id = item.purchase_order.id
    
    item.delete()
    
    messages.success(request, f'Item {item.product.name} dihapus dari PO')
    return redirect('purchases:purchase_order_add_item', po_id=po_id)


@login_required
def purchase_order_submit(request, pk):
    """
    Change purchase order status to SENT
    """
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if po.status != 'DRAFT':
        messages.error(request, 'Purchase Order sudah dikirim atau diterima')
        return redirect('purchases:purchase_order_detail', pk=pk)
    
    po.status = 'SENT'
    po.save()
    
    messages.success(request, f'Purchase Order {po.po_number} berhasil dikirim')
    return redirect('purchases:purchase_order_detail', pk=pk)


@login_required
def goods_receipt_list(request):
    # Check if user has permission to access goods receipts
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    grns = GoodsReceipt.objects.all().order_by('-received_at')
    return render(request, 'purchases/goods_receipt_list.html', {'grns': grns})


@login_required
def goods_receipt_create(request):
    if request.method == 'POST':
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            grn = form.save()
            messages.success(request, f'Goods Receipt {grn.grn_number} berhasil dibuat')
            return redirect('purchases:goods_receipt_detail', pk=grn.id)
    else:
        # Generate new GRN number
        latest_grn = GoodsReceipt.objects.order_by('-id').first()
        next_number = 1 if not latest_grn else latest_grn.id + 1
        grn_number = f"GRN-{next_number:06d}"
        form = GoodsReceiptForm(initial={'grn_number': grn_number})
    
    return render(request, 'purchases/goods_receipt_form.html', {'form': form})


@login_required
def goods_receipt_detail(request, pk):
    grn = get_object_or_404(GoodsReceipt, pk=pk)
    po_items = []
    if grn.purchase_order:
        po_items = POItem.objects.filter(purchase_order=grn.purchase_order).select_related('product')
    
    return render(request, 'purchases/goods_receipt_detail.html', {
        'grn': grn,
        'po_items': po_items
    })


@login_required
def receive_purchase_order(request, po_id):
    """
    Create goods receipt for a purchase order
    """
    po = get_object_or_404(PurchaseOrder, id=po_id)
    
    if request.method == 'POST':
        # Create goods receipt
        grn_number = request.POST.get('grn_number')
        warehouse_id = request.POST.get('warehouse')
        
        # Validate warehouse
        if str(po.warehouse.id) != warehouse_id:
            messages.error(request, 'Gudang pada GRN harus sama dengan gudang pada PO')
            return redirect('purchases:receive_purchase_order', po_id=po_id)
        
        grn = GoodsReceipt.objects.create(
            grn_number=grn_number,
            purchase_order=po,
            warehouse_id=warehouse_id
        )
        
        # Update PO status
        po.status = 'RECEIVED'
        po.save()
        
        # Update stock for each item in the PO
        for po_item in po.items.all():
            update_stock(
                product_id=po_item.product.id,
                warehouse_id=po.warehouse.id,
                qty_change=po_item.qty,
                ref_type='GRN',
                ref_id=grn.id
            )
        
        messages.success(request, f'Barang dari PO {po.po_number} berhasil diterima di GRN {grn.grn_number}')
        return redirect('purchases:goods_receipt_detail', pk=grn.id)
    
    # Generate new GRN number
    latest_grn = GoodsReceipt.objects.order_by('-id').first()
    next_number = 1 if not latest_grn else latest_grn.id + 1
    grn_number = f"GRN-{next_number:06d}"
    
    context = {
        'po': po,
        'po_items': po.items.all().select_related('product'),
        'grn_number': grn_number
    }
    return render(request, 'purchases/receive_purchase_order.html', context)