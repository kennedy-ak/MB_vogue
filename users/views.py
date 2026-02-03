from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserProfileForm
from core.models import Order


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'users/register.html', context)


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to next page if specified
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('core:home')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'users/login.html', context)


def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)[:5]

    context = {
        'orders': orders,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)

    context = {
        'form': form,
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).select_related('payment')

    context = {
        'orders': orders,
    }
    return render(request, 'users/order_history.html', context)
