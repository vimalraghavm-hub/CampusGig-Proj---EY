from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Gig, Order, Message, CartItem
from .forms import GigForm
from django.contrib import messages
from django.db import models




def index(request):
    categories = Category.objects.all()[:6]
    return render(request, 'index.html', {'categories': categories})

def gig_list(request, category_slug=None):
    category = None
    gigs = Gig.objects.all()
    query = request.GET.get('q')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        gigs = gigs.filter(category=category)
    
    if query:
        gigs = gigs.filter(
            models.Q(title__icontains=query) | models.Q(description__icontains=query)
        )
        
    return render(request, 'platform/gig_list.html', {
        'category': category, 
        'gigs': gigs,
        'query': query
    })


@login_required
def create_gig(request):
    if not request.user.is_freelancer and not request.user.is_superuser:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = GigForm(request.POST, request.FILES)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.user = request.user
            gig.save()
            return redirect('dashboard')
    else:
        form = GigForm()
    return render(request, 'platform/gig_form.html', {'form': form})

def gig_detail(request, pk):
    gig_obj = get_object_or_404(Gig, pk=pk)
    return render(request, 'platform/gig_detail_v2.html', {'gig_item': gig_obj})

@login_required
def create_order(request, gig_id):
    gig = get_object_or_404(Gig, pk=gig_id)
    if request.user == gig.user:
        return redirect('gig_detail', pk=gig_id)
    
    order = Order.objects.create(
        gig=gig,
        client=request.user,
        status='pending'
    )
    return redirect('order_detail', pk=order.pk)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user != order.client and request.user != order.gig.user and not request.user.is_superuser:
        return redirect('dashboard')
    
    messages = order.messages.all().order_by('timestamp')
    
    return render(request, 'platform/order_detail.html', {
        'order': order,
        'chat_messages': messages
    })

@login_required
def send_message(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.user != order.client and request.user != order.gig.user:
        return redirect('dashboard')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            receiver = order.gig.user if request.user == order.client else order.client
            Message.objects.create(
                order=order,
                sender=request.user,
                receiver=receiver,
                content=content
            )
    return redirect('order_detail', pk=order_id)

@login_required
def update_order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)
    if request.user == order.gig.user:
        if status in ['in_progress', 'completed']:
            order.status = status
            order.save()
    elif request.user == order.client and status == 'cancelled':
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            
    return redirect('order_detail', pk=pk)

@login_required
def my_gigs(request):
    if request.user.is_superuser:
        gigs = Gig.objects.all().order_by('-created_at')
        is_admin = True
    else:
        if not request.user.is_freelancer:
            return redirect('dashboard')
        gigs = Gig.objects.filter(user=request.user).order_by('-created_at')
        is_admin = False
    return render(request, 'platform/my_gigs.html', {'gigs': gigs, 'is_admin': is_admin})

@login_required
def my_purchases(request):
    if request.user.is_superuser:
        orders = Order.objects.all().order_by('-created_at')
        is_admin = True
    else:
        orders = Order.objects.filter(client=request.user).order_by('-created_at')
        is_admin = False
    return render(request, 'platform/my_purchases.html', {'orders': orders, 'is_admin': is_admin})

@login_required
def cart_view(request):
    c_items = CartItem.objects.filter(user=request.user)
    t_price = sum(item.gig.price for item in c_items)
    return render(request, 'platform/cart_v2.html', {
        'v2_cart_items': c_items,
        'v2_total': t_price
    })

@login_required
def add_to_cart(request, gig_id):
    if request.method == 'POST':
        gig = get_object_or_404(Gig, pk=gig_id)
        if gig.user == request.user:
            messages.warning(request, "Marketing your own services? You cannot add your own gig to the cart.")
        else:
            CartItem.objects.get_or_create(user=request.user, gig=gig)
            messages.success(request, f"'{gig.title}' has been added to your cart!")
        return redirect('cart')
    return redirect('gig_detail', pk=gig_id)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cart')
    
    for item in cart_items:
        Order.objects.create(
            gig=item.gig,
            client=request.user,
            status='pending'
        )
    
    cart_items.delete()
    messages.success(request, "Order(s) placed successfully!")
    return redirect('my_purchases')

@login_required
def edit_gig(request, pk):
    gig = get_object_or_404(Gig, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GigForm(request.POST, request.FILES, instance=gig)
        if form.is_valid():
            form.save()
            messages.success(request, "Gig updated successfully!")
            return redirect('my_gigs')
    else:
        form = GigForm(instance=gig)
    return render(request, 'platform/gig_form.html', {'form': form, 'is_edit': True})


from django.http import JsonResponse

def api_gig_list(request):
    gigs = Gig.objects.all()
    data = [
        {
            'id': gig.id,
            'title': gig.title,
            'price': float(gig.price),
            'user': gig.user.username,
            'category': gig.category.name if gig.category else None
        } for gig in gigs
    ]
    return JsonResponse({'gigs': data})

def api_category_list(request):
    categories = Category.objects.all()
    data = [
        {
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'icon': cat.icon
        } for cat in categories
    ]
    return JsonResponse({'categories': data})
