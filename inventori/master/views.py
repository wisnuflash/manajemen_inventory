from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Category, Product, Supplier, Customer
from .forms import CategoryForm, ProductForm, SupplierForm, CustomerForm


# Category CRUD
@login_required
def category_list(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/category_list.html', {'page_obj': page_obj})

@login_required
def category_create(request):
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
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('master:category_list')
    return render(request, 'master/category_confirm_delete.html', {'category': category})


# Product CRUD
@login_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/product_list.html', {'page_obj': page_obj})

@login_required
def product_create(request):
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
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('master:product_list')
    return render(request, 'master/product_confirm_delete.html', {'product': product})


# Supplier CRUD
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    paginator = Paginator(suppliers, 10)  # Show 10 suppliers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/supplier_list.html', {'page_obj': page_obj})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('master:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'master/supplier_form.html', {'form': form})

@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('master:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'master/supplier_form.html', {'form': form, 'supplier': supplier})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('master:supplier_list')
    return render(request, 'master/supplier_confirm_delete.html', {'supplier': supplier})


# Customer CRUD
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'master/customer_list.html', {'page_obj': page_obj})

@login_required
def customer_create(request):
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
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('master:customer_list')
    return render(request, 'master/customer_confirm_delete.html', {'customer': customer})