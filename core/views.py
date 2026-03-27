from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import UserRegistrationForm, UserLoginForm
from platform_app.models import Gig, Order


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CampusGig, {user.username}!")
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard_view(request):
    user_gigs = []
    if request.user.is_freelancer:
        user_gigs = Gig.objects.filter(user=request.user)
    
    # Orders where user is client or freelancer
    active_orders = Order.objects.filter(
        Q(client=request.user) | Q(gig__user=request.user)
    ).exclude(status__in=['completed', 'cancelled']).order_by('-created_at')
    
    recent_orders = Order.objects.filter(
        Q(client=request.user) | Q(gig__user=request.user)
    ).order_by('-created_at')[:5]

    context = {
        'user_gigs': user_gigs,
        'active_orders': active_orders,
        'recent_orders': recent_orders,
    }

    # God-Mode for Admins
    if request.user.is_superuser:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context['is_admin'] = True
        context['total_platform_users'] = User.objects.count()
        context['total_platform_gigs'] = Gig.objects.count()
        context['total_platform_orders'] = Order.objects.count()
        # Get 10 most recent global orders for admin overview
        context['global_recent_orders'] = Order.objects.all().order_by('-created_at')[:10]

    return render(request, 'core/dashboard.html', context)

