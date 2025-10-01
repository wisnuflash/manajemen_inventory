from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.core.exceptions import PermissionDenied
from .models import Warehouse, Stock, StockMove, ReorderPolicy
from .forms import WarehouseForm, StockForm, StockMoveForm, ReorderPolicyForm
from master.models import Product


@login_required
def warehouse_list(request):
    # Check if user has permission to access warehouses
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    warehouses = Warehouse.objects.all()
    return render(request, 'inventory/warehouse_list.html', {'warehouses': warehouses})


@login_required
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Warehouse created successfully.')
            return redirect('inventory:warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'inventory/warehouse_form.html', {'form': form})


@login_required
def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Warehouse updated successfully.')
            return redirect('inventory:warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'inventory/warehouse_form.html', {'form': form, 'warehouse': warehouse})


@login_required
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, 'Warehouse deleted successfully.')
        return redirect('inventory:warehouse_list')
    return render(request, 'inventory/warehouse_confirm_delete.html', {'warehouse': warehouse})


@login_required
def stock_list(request):
    # Check if user has permission to access stocks
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    # Get filter parameters
    warehouse_id = request.GET.get('warehouse')
    product_id = request.GET.get('product')
    
    stocks = Stock.objects.select_related('product', 'warehouse').all()
    
    # Apply filters
    if warehouse_id:
        stocks = stocks.filter(warehouse_id=warehouse_id)
    if product_id:
        stocks = stocks.filter(product_id=product_id)
    
    # Get all warehouses and products for filter dropdown
    warehouses = Warehouse.objects.all()
    products = Product.objects.filter(is_active=True)
    
    return render(request, 'inventory/stock_list.html', {
        'stocks': stocks,
        'warehouses': warehouses,
        'products': products,
        'selected_warehouse': warehouse_id,
        'selected_product': product_id
    })


@login_required
def stock_adjustment(request):
    """
    Manual stock adjustment view
    """
    # Check if user has permission to access stock adjustment
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    if request.method == 'POST':
        product_id = request.POST.get('product')
        warehouse_id = request.POST.get('warehouse')
        adjustment_type = request.POST.get('adjustment_type')  # 'in' or 'out'
        qty = int(request.POST.get('qty', 0))
        note = request.POST.get('note', '')
        
        product = get_object_or_404(Product, id=product_id)
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        
        # Get or create stock record
        stock, created = Stock.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={'qty': 0}
        )
        
        # Update quantity based on adjustment type
        if adjustment_type == 'in':
            stock.qty += qty
            qty_in = qty
            qty_out = 0
        else:
            stock.qty = max(0, stock.qty - qty)  # Prevent negative stock
            qty_in = 0
            qty_out = qty
        
        stock.save()
        
        # Create stock movement record
        StockMove.objects.create(
            product=product,
            warehouse=warehouse,
            ref_type='ADJUST',
            qty_in=qty_in,
            qty_out=qty_out,
            note=note
        )
        
        messages.success(request, f'Stock adjustment for {product.name} completed successfully.')
        return redirect('inventory:stock_list')
    
    # For GET request, show the adjustment form
    warehouses = Warehouse.objects.all()
    products = Product.objects.filter(is_active=True)
    
    return render(request, 'inventory/stock_adjustment.html', {
        'warehouses': warehouses,
        'products': products
    })


@login_required
def stock_movement_list(request):
    # Check if user has permission to access stock movements
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    movements = StockMove.objects.select_related('product', 'warehouse').all().order_by('-moved_at')
    return render(request, 'inventory/stock_movement_list.html', {'movements': movements})


@login_required
def reorder_policy_list(request):
    # Check if user has permission to access reorder policies
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    policies = ReorderPolicy.objects.select_related('product', 'warehouse').all()
    return render(request, 'inventory/reorder_policy_list.html', {'policies': policies})


@login_required
def reorder_policy_create(request):
    if request.method == 'POST':
        form = ReorderPolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reorder policy created successfully.')
            return redirect('inventory:reorder_policy_list')
    else:
        form = ReorderPolicyForm()
    return render(request, 'inventory/reorder_policy_form.html', {'form': form})


@login_required
def reorder_policy_update(request, pk):
    policy = get_object_or_404(ReorderPolicy, pk=pk)
    if request.method == 'POST':
        form = ReorderPolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reorder policy updated successfully.')
            return redirect('inventory:reorder_policy_list')
    else:
        form = ReorderPolicyForm(instance=policy)
    return render(request, 'inventory/reorder_policy_form.html', {'form': form, 'policy': policy})


@login_required
def low_stock_alerts(request):
    """
    Show items with stock levels below minimum or ROP
    """
    # Check if user has permission to access low stock alerts
    if request.user.role not in ['warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    # Get all stocks that are below the product's minimum stock level
    low_stocks = Stock.objects.select_related('product', 'warehouse').filter(
        Q(qty__lte=0) | Q(qty__lte=models.F('product__min_stock'))
    )
    
    # Also check against ROP (Reorder Point) if exists
    rop_alerts = []
    for stock in low_stocks:
        try:
            rop_policy = ReorderPolicy.objects.get(
                product=stock.product,
                warehouse=stock.warehouse
            )
            if stock.qty <= rop_policy.rop:
                rop_alerts.append({
                    'stock': stock,
                    'rop': rop_policy.rop,
                    'reorder_qty': rop_policy.reorder_qty
                })
        except ReorderPolicy.DoesNotExist:
            # If no ROP policy, just show as low stock
            rop_alerts.append({
                'stock': stock,
                'rop': 'N/A',
                'reorder_qty': 'N/A'
            })
    
    return render(request, 'inventory/low_stock_alerts.html', {'rop_alerts': rop_alerts})