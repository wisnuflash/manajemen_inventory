from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import Sale, SaleItem
from .forms import POSForm, SaleItemForm
from master.models import Product
from inventory.models import Stock, StockMove
from inventory.services import update_stock
import uuid
from datetime import datetime
from decimal import Decimal


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
    Unified POS (Point of Sale) view for cashiers - all steps in one page
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
    
    # Get existing draft transactions
    draft_sales = Sale.objects.filter(status='DRAFT').order_by('-id')
    
    context = {
        'draft_sales': draft_sales,
        'form': POSForm(),  # For creating new transactions
    }
    return render(request, 'sales/pos.html', context)


@login_required
def pos_unified(request, sale_id=None):
    """
    Unified POS view - all steps in one page
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
    
    if sale_id:
        # Continue existing sale
        sale = get_object_or_404(Sale, id=sale_id, status='DRAFT')
        form = POSForm(instance=sale)
    else:
        # New sale
        sale = None
        form = POSForm()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_sale':
            # Create new sale
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
                    return redirect('sales:pos_unified', sale_id=existing_draft.id)
                
                # Generate unique invoice number
                invoice_number = generate_unique_invoice_number()
                
                sale = form.save(commit=False)
                sale.status = 'DRAFT'
                sale.invoice_number = invoice_number
                sale.save()
                messages.success(request, f'Transaksi dimulai dengan invoice: {sale.invoice_number}')
                return redirect('sales:pos_unified', sale_id=sale.id)
                
        elif action == 'add_item':
            # Add item to sale
            if not sale:
                messages.error(request, 'Tidak ada transaksi aktif')
                return redirect('sales:pos_unified')
                
            product_sku = request.POST.get('product_sku')
            qty = int(request.POST.get('qty', 1))
            
            try:
                product = Product.objects.get(sku=product_sku, is_active=True)
            except Product.DoesNotExist:
                messages.error(request, f'Produk dengan SKU {product_sku} tidak ditemukan')
                return redirect('sales:pos_unified', sale_id=sale.id)
            
            # Create sale item
            item = SaleItem.objects.create(
                sale=sale,
                product=product,
                qty=qty,
                price=product.price
            )
            
            # Update total amount
            sale.total_amount += item.get_total()
            sale.save()
            
            messages.success(request, f'{item.qty} {product.name} ditambahkan ke keranjang')
            return redirect('sales:pos_unified', sale_id=sale.id)
            
        elif action == 'remove_item':
            # Remove item from sale
            if not sale:
                messages.error(request, 'Tidak ada transaksi aktif')
                return redirect('sales:pos_unified')
                
            item_id = request.POST.get('item_id')
            item = get_object_or_404(SaleItem, id=item_id, sale=sale)
            
            # Update total amount
            sale.total_amount -= item.get_total()
            sale.save()
            
            item.delete()
            messages.success(request, f'Item {item.product.name} dihapus dari keranjang')
            return redirect('sales:pos_unified', sale_id=sale.id)
            
        elif action == 'cancel_sale':
            # Cancel and delete sale
            if sale:
                invoice_number = sale.invoice_number
                sale.delete()
                messages.success(request, f'Transaksi {invoice_number} dibatalkan')
            return redirect('sales:pos')
            
        elif action == 'complete_sale':
            # Complete sale with payment
            if not sale:
                messages.error(request, 'Tidak ada transaksi aktif')
                return redirect('sales:pos_unified')
                
            total_payment = Decimal(request.POST.get('total_payment', '0'))
            
            if total_payment < sale.total_amount:
                messages.error(request, 'Pembayaran tidak mencukupi')
                return redirect('sales:pos_unified', sale_id=sale.id)
            
            # Complete the sale
            with transaction.atomic():
                sale.status = 'PAID'
                sale.save()
                
                # Update stock for each item
                for item in sale.items.all():
                    update_stock(item.product.id, sale.warehouse.id, -item.qty, 'SALE', sale.id)
            
            messages.success(request, f'Transaksi {sale.invoice_number} berhasil diselesaikan')
            return redirect('sales:pos_receipt', sale_id=sale.id)
    
    # Get current items in the sale
    if sale:
        sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
        total_amount = sum(item.get_total() for item in sale_items)
    else:
        sale_items = []
        total_amount = Decimal('0')
    
    context = {
        'sale': sale,
        'sale_items': sale_items,
        'total_amount': total_amount,
        'form': form,
        'draft_sales': Sale.objects.filter(status='DRAFT').exclude(id=sale.id if sale else None).order_by('-id') if sale else Sale.objects.filter(status='DRAFT').order_by('-id'),
    }
    return render(request, 'sales/pos_unified.html', context)


@login_required
def pos_receipt(request, sale_id):
    """
    Show receipt after sale completion
    """
    # Check if user has permission to access POS
    if request.user.role not in ['cashier', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    sale = get_object_or_404(Sale, id=sale_id, status='PAID')
    sale_items = SaleItem.objects.filter(sale=sale).select_related('product')
    
    context = {
        'sale': sale,
        'sale_items': sale_items,
        'total_amount': sum(item.get_total() for item in sale_items),
    }
    return render(request, 'sales/pos_receipt.html', context)


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
    
    query = request.GET.get('q', '').strip()
    start_date_param = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    
    sales = (Sale.objects
             .select_related('customer', 'warehouse')
             .order_by('-sold_at'))
    
    if query:
        sales = sales.filter(
            Q(invoice_number__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(warehouse__name__icontains=query)
        )
    
    if start_date_param:
        try:
            start_date = datetime.strptime(start_date_param, "%Y-%m-%d").date()
            sales = sales.filter(sold_at__date__gte=start_date)
        except ValueError:
            start_date_param = ''
    
    if end_date_param:
        try:
            end_date = datetime.strptime(end_date_param, "%Y-%m-%d").date()
            sales = sales.filter(sold_at__date__lte=end_date)
        except ValueError:
            end_date_param = ''
    
    context = {
        'sales': sales,
        'q': query,
        'start_date': start_date_param or '',
        'end_date': end_date_param or '',
    }
    return render(request, 'sales/sale_list.html', context)


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
