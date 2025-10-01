from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserForm

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'registration/register.html')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'registration/register.html')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='cashier'  # Default role
                )
                user.save()
                messages.success(request, 'Account created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/register.html')
    else:
        return render(request, 'registration/register.html')

@login_required
def profile(request):
    # Profile is accessible to all users
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def user_list(request):
    """
    List all users - only accessible to admin role
    """
    if request.user.role != 'admin':
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def user_create(request):
    """
    Create a new user - only accessible to admin role
    """
    if request.user.role != 'admin':
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'User {user.username} berhasil dibuat.')
            return redirect('accounts:user_list')
    else:
        form = UserForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Tambah User'})

@login_required
def user_update(request, user_id):
    """
    Update a user - only accessible to admin role
    """
    if request.user.role != 'admin':
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            # Handle password separately if provided
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
                user.save()
            else:
                form.save()
            messages.success(request, f'User {user.username} berhasil diperbarui.')
            return redirect('accounts:user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'Edit User: {user.username}', 'user_obj': user})

@login_required
def user_delete(request, user_id):
    """
    Delete a user - only accessible to admin role
    """
    if request.user.role != 'admin':
        raise PermissionDenied("Anda tidak memiliki akses ke fitur ini.")
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} berhasil dihapus.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})