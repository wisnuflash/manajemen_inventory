from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from sales.models import Sale, SaleItem
from inventory.models import Stock, ReorderPolicy
from purchases.models import PurchaseOrder
from mining.models import AssociationRule
from master.models import Product
from datetime import datetime, timedelta


@login_required
def dashboard(request):
    """Main dashboard view with KPIs and charts"""
    
    # Calculate KPIs
    # Sales today
    today = datetime.now().date()
    sales_today = Sale.objects.filter(
        sold_at__date=today,
        status='PAID'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Sales this week
    week_start = today - timedelta(days=today.weekday())
    sales_week = Sale.objects.filter(
        sold_at__date__gte=week_start,
        status='PAID'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Sales this month
    month_start = today.replace(day=1)
    sales_month = Sale.objects.filter(
        sold_at__date__gte=month_start,
        status='PAID'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Inventory value
    inventory_value = Stock.objects.select_related('product').aggregate(
        total=Sum(F('qty') * F('product__price'))
    )['total'] or 0
    
    # Low stock items
    low_stock_count = Stock.objects.filter(
        qty__lte=F('product__min_stock')
    ).count()
    
    # ROP alerts
    rop_alerts = []
    for stock in Stock.objects.select_related('product', 'warehouse'):
        try:
            rop_policy = ReorderPolicy.objects.get(
                product=stock.product,
                warehouse=stock.warehouse
            )
            if stock.qty <= rop_policy.rop:
                rop_alerts.append({
                    'product': stock.product.name,
                    'warehouse': stock.warehouse.name,
                    'current_qty': stock.qty,
                    'rop': rop_policy.rop,
                    'reorder_qty': rop_policy.reorder_qty
                })
        except ReorderPolicy.DoesNotExist:
            # If no ROP policy but stock is low, still count it
            if stock.qty <= stock.product.min_stock:
                rop_alerts.append({
                    'product': stock.product.name,
                    'warehouse': stock.warehouse.name,
                    'current_qty': stock.qty,
                    'rop': 'N/A',
                    'reorder_qty': 'N/A'
                })
    
    # Open POs
    open_pos = PurchaseOrder.objects.filter(
        status__in=['DRAFT', 'SENT']
    )
    
    # Top selling products (last month)
    top_products = SaleItem.objects.filter(
        sale__sold_at__date__gte=month_start,
        sale__status='PAID'
    ).values(
        'product__sku',
        'product__name'
    ).annotate(
        total_qty=Sum('qty'),
        total_revenue=Sum(F('qty') * F('price'))
    ).order_by('-total_qty')[:10]
    
    # Top association rules
    top_rules = AssociationRule.objects.order_by('-lift')[:10]
    
    context = {
        'sales_today': sales_today,
        'sales_week': sales_week,
        'sales_month': sales_month,
        'inventory_value': inventory_value,
        'low_stock_count': low_stock_count,
        'rop_alerts': rop_alerts,
        'open_pos': open_pos,
        'top_products': top_products,
        'top_rules': top_rules,
    }
    return render(request, 'summary/dashboard.html', context)


# API views for dashboard charts
@login_required
def api_top_products(request):
    """API endpoint for top products chart"""
    # Check if user has permission to access dashboard data
    if request.user.role not in ['cashier', 'warehouse', 'manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    period = request.GET.get('period', 'month')  # month, week, day
    
    today = datetime.now().date()
    
    if period == 'month':
        start_date = today.replace(day=1)
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
    else:  # default to day
        start_date = today
    
    top_products = SaleItem.objects.filter(
        sale__sold_at__date__gte=start_date,
        sale__status='PAID'
    ).values(
        'product__sku',
        'product__name'
    ).annotate(
        total_qty=Sum('qty'),
        total_revenue=Sum(F('qty') * F('price'))
    ).order_by('-total_qty')[:10]
    
    data = []
    for item in top_products:
        data.append({
            'sku': item['product__sku'],
            'name': item['product__name'],
            'qty': item['total_qty'],
            'revenue': float(item['total_revenue']) if item['total_revenue'] else 0
        })
    
    return JsonResponse({'products': data})


# @login_required
def api_top_rules(request):
    """API endpoint for top rules chart"""
    # Check if user has permission to access mining data
    # if request.user.role not in ['analyst', 'manager', 'admin']:
    #     raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    top_rules = AssociationRule.objects.order_by('-lift')[:10]
    
    data = []
    for rule in top_rules:
        data.append({
            'antecedent': rule.get_antecedent_list(),
            'consequent': rule.get_consequent_list(),
            'support': float(rule.support),
            'confidence': float(rule.confidence),
            'lift': float(rule.lift),
            'rule_text': f"{', '.join(rule.get_antecedent_list())} → {', '.join(rule.get_consequent_list())}"
        })
    
    return JsonResponse({'rules': data})