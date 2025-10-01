from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import Sale, SaleItem
from .forms import POSForm, SaleItemForm
from master.models import Product
from inventory.models import Stock, StockMove
from inventory.services import update_stock
import uuid
from datetime import datetime


def generate_unique_invoice_number():
    """
    Generate a unique invoice number that doesn't conflict with existing ones
    """
    # Try timestamp-based approach first
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    invoice_number = f"INV-{timestamp}"
    
    # Check if this invoice number already exists
    counter = 1
    original_invoice_number = invoice_number
    while Sale.objects.filter(invoice_number=invoice_number).exists():
        invoice_number = f"{original_invoice_number}-{counter:03d}"
        counter += 1
    
    return invoice_number


@login_required
def pos_view(request):
    """
    POS (Point of Sale) view for cashiers
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    form = POSForm()
    
    if request.method == 'POST':
        # Handle POS form submission
        form = POSForm(request.POST)
        if form.is_valid():
            # Check if there's already a draft sale with the same customer and warehouse
            existing_draft = Sale.objects.filter(
                status='DRAFT',
                customer=form.cleaned_data.get('customer'),
                warehouse=form.cleaned_data.get('warehouse')
            ).first()
            
            if existing_draft:
                messages.warning(request, f'Anda sudah memiliki transaksi draft untuk customer dan gudang ini: {existing_draft.invoice_number}. Silakan lanjutkan transaksi tersebut.')
                return redirect('sales:pos_add_item', sale_id=existing_draft.id)
            
            # Generate unique invoice number
            invoice_number = generate_unique_invoice_number()
            
            sale = form.save(commit=False)
            sale.status = 'DRAFT'  # Start with DRAFT status
            sale.invoice_number = invoice_number
            sale.save()
            messages.success(request, f'Sale started with invoice: {sale.invoice_number}')
            return redirect('sales:pos_add_item', sale_id=sale.id)
    else:
        # Just create an empty form without initial data
        form = POSForm()
    
    # Get existing draft transactions for all users (not just current user)
    draft_sales = Sale.objects.filter(status='DRAFT').order_by('-id')
    
    context = {
        'form': form,
        'draft_sales': draft_sales,
    }
    return render(request, 'sales/pos.html', context)


@login_required
def pos_cancel_sale(request, sale_id):
    """
    Cancel and delete a POS sale
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Only allow cancelling DRAFT sales
    if sale.status != 'DRAFT':
        messages.error(request, f'Penjualan dengan status {sale.get_status_display()} tidak dapat dibatalkan')
        return redirect('sales:pos_add_item', sale_id=sale.id)
    
    sale.delete()
    messages.success(request, f'Penjualan dibatalkan dan dihapus')
    return redirect('sales:pos')


@login_required
def pos_add_item(request, sale_id):
    """
    Add item to POS sale
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sale = get_object_or_404(Sale, id=sale_id)
    
    if request.method == 'POST':
        action = request.POST.get('action', 'add_item')
        
        if action == 'cancel':
            # Delete the sale and all related items
            sale.delete()
            messages.success(request, f'Penjualan dibatalkan dan dihapus')
            return redirect('sales:pos')
        
        form = SaleItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            
            # Get product by SKU
            product_sku = request.POST.get('product_sku')
            try:
                product = Product.objects.get(sku=product_sku, is_active=True)
            except Product.DoesNotExist:
                messages.error(request, f'Produk dengan SKU {product_sku} tidak ditemukan')
                return redirect('sales:pos_add_item', sale_id=sale_id)
            
            # Set the product and price
            item.product = product
            item.price = product.price
            item.sale = sale
            item.save()
            
            # Update total amount
            sale.total_amount += item.get_total()
            sale.save()
            
            messages.success(request, f'{item.qty} {product.name} ditambahkan ke keranjang')
            return redirect('sales:pos_add_item', sale_id=sale_id)
    else:
        form = SaleItemForm()
    
    # Get current items in the sale
    sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
    total_amount = sum(item.get_total() for item in sale_items)
    
    context = {
        'sale': sale,
        'form': form,
        'sale_items': sale_items,
        'total_amount': total_amount,
    }
    return render(request, 'sales/pos_add_item.html', context)


@login_required
def pos_complete_sale(request, sale_id):
    """
    Complete the POS sale (change status to PAID)
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sale = get_object_or_404(Sale, id=sale_id)
    
    if request.method == 'POST':
        action = request.POST.get('action', 'complete')
        
        if action == 'cancel':
            # Delete the sale and all related items
            sale.delete()
            messages.success(request, f'Penjualan dibatalkan dan dihapus')
            return redirect('sales:pos')
        else:
            with transaction.atomic():
                # Change status to PAID
                sale.status = 'PAID'
                sale.save()
                
                # For each item in the sale, update stock and create stock moves
                for item in sale.items.all():
                    # Update stock
                    update_stock(item.product.id, sale.warehouse.id, -item.qty, 'SALE', sale.id)
                
            messages.success(request, f'Penjualan {sale.invoice_number} berhasil diselesaikan')
            return redirect('sales:sale_detail', pk=sale.id)
    
    sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
    total_amount = sum(item.get_total() for item in sale_items)
    
    context = {
        'sale': sale,
        'sale_items': sale_items,
        'total_amount': total_amount,
    }
    return render(request, 'sales/pos_complete.html', context)


@login_required
def remove_sale_item(request, item_id):
    """
    Remove an item from the current sale
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    item = get_object_or_404(SaleItem, id=item_id)
    sale_id = item.sale.id
    
    # Update the total amount of the sale
    sale = item.sale
    sale.total_amount -= item.get_total()
    sale.save()
    
    item.delete()
    
    messages.success(request, f'Item {item.product.name} dihapus dari keranjang')
    return redirect('sales:pos_add_item', sale_id=sale_id)


@login_required
@csrf_exempt
def search_product_ajax(request):
    """
    AJAX endpoint to search for products by SKU
    """
    if request.method == 'GET':
        sku = request.GET.get('sku', '')
        warehouse_id = request.GET.get('warehouse_id', '')
        
        try:
            product = Product.objects.get(sku=sku, is_active=True)
            # Get the available stock
            stock_qty = 0
            if warehouse_id:
                try:
                    warehouse_id = int(warehouse_id)
                    stock = Stock.objects.filter(
                        product=product,
                        warehouse_id=warehouse_id
                    ).first()
                    stock_qty = stock.qty if stock else 0
                except (ValueError, TypeError):
                    # If warehouse_id is not a valid integer, set stock_qty to 0
                    stock_qty = 0
            
            return JsonResponse({
                'success': True,
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'stock': stock_qty,
                'sku': product.sku
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Produk dengan SKU {sku} tidak ditemukan'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# Additional views for managing sales
@login_required
def sale_list(request):
    # Check if user has permission to access sales list
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sales = Sale.objects.all().order_by('-sold_at')
    return render(request, 'sales/sale_list.html', {'sales': sales})


@login_required
def sale_detail(request, pk):
    # Check if user has permission to access sales
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sale = get_object_or_404(Sale, pk=pk)
    sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
    return render(request, 'sales/sale_detail.html', {
        'sale': sale,
        'sale_items': sale_items
    })