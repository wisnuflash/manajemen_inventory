from .models import Stock, StockMove


def update_stock(product_id, warehouse_id, qty_change, ref_type, ref_id):
    """
    Update stock quantity and create a stock movement record
    """
    # Get or create the stock record
    stock, created = Stock.objects.get_or_create(
        product_id=product_id,
        warehouse_id=warehouse_id,
        defaults={'qty': 0}
    )
    
    # Calculate new quantity
    new_qty = stock.qty + qty_change
    if new_qty < 0:
        new_qty = 0  # Don't allow negative stock
    
    # Update the stock
    stock.qty = new_qty
    stock.save()
    
    # Create a stock movement record
    if qty_change > 0:
        qty_in = qty_change
        qty_out = 0
    else:
        qty_in = 0
        qty_out = abs(qty_change)
    
    StockMove.objects.create(
        product_id=product_id,
        warehouse_id=warehouse_id,
        ref_type=ref_type,
        ref_id=ref_id,
        qty_in=qty_in,
        qty_out=qty_out,
        note=f'Stock update via {ref_type}'
    )
    
    return stock