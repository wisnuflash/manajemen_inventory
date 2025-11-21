from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .models import Category, Product, Customer
from .forms import CategoryForm, ProductForm, CustomerForm


# Category CRUD
@login_required
def category_list(request):
    # Check if user has permission to access categories
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    categories = Category.objects.all()
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/category_list.html', {'page_obj': page_obj})

@login_required
def category_create(request):
    # Check if user has permission to create categories
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('master:category_list')
    else:
        form = CategoryForm()
    return render(request, 'master/category_form.html', {'form': form})

@login_required
def category_update(request, pk):
    # Check if user has permission to update categories
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('master:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'master/category_form.html', {'form': form, 'category': category})

@login_required
def category_delete(request, pk):
    # Check if user has permission to delete categories
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('master:category_list')
    return render(request, 'master/category_confirm_delete.html', {'category': category})


# Product CRUD
@login_required
def product_list(request):
    # Check if user has permission to access products
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    products = Product.objects.select_related('category').all()
    paginator = Paginator(products, 20)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/product_list.html', {'page_obj': page_obj})

@login_required
def product_create(request):
    # Check if user has permission to create products
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('master:product_list')
    else:
        form = ProductForm()
    return render(request, 'master/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    # Check if user has permission to update products
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('master:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'master/product_form.html', {'form': form, 'product': product})

@login_required
def product_delete(request, pk):
    # Check if user has permission to delete products
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('master:product_list')
    return render(request, 'master/product_confirm_delete.html', {'product': product})


# Customer CRUD
@login_required
def customer_list(request):
    # Check if user has permission to access customers
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    customers = Customer.objects.all()
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/customer_list.html', {'page_obj': page_obj})

@login_required
def customer_create(request):
    # Check if user has permission to create customers
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully.')
            return redirect('master:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'master/customer_form.html', {'form': form})

@login_required
def customer_update(request, pk):
    # Check if user has permission to update customers
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('master:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'master/customer_form.html', {'form': form, 'customer': customer})

@login_required
def customer_delete(request, pk):
    # Check if user has permission to delete customers
    if request.user.role not in ['manager', 'admin']:
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
        
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('master:customer_list')
    return render(request, 'master/customer_confirm_delete.html', {'customer': customer})