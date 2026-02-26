from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def get_cart(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )
    return cart


def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'login_required'
        })

    product = get_object_or_404(Product, id=product_id)

    cart = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1

    item.save()

    return JsonResponse({
        'status': 'success',
        'qty': item.quantity
    })

@require_POST
def increase_qty(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    item.quantity += 1
    item.save()

    return JsonResponse({
        "status": "success",
        "qty": item.quantity,
        "total": item.total_price()
    })


@require_POST
def decrease_qty(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()

    return JsonResponse({
        "status": "success",
        "qty": item.quantity,
        "total": item.total_price()
    })


@require_POST
def remove_item(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    item.delete()

    return JsonResponse({
        "status": "removed"
    })

def view_cart(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart = get_cart(request)

    items = CartItem.objects.filter(cart=cart)

    total = sum(i.total_price() for i in items)

    return render(request, 'orders/cart.html', {
        'items': items,
        'total': total
    })

def checkout(request):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart = get_cart(request)
    
    items = CartItem.objects.filter(cart=cart)
    
    if not items:
        return redirect('home')
    
    if request.method == "POST":
        
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']
        
        total = sum(i.total_price() for i in items)
        
        order = Order.objects.create(
            user = request.user,
            full_name=name,
            phone=phone,
            address=address,
            total_amount=total
        )
        
        for item in items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            
        # Clear cart
        items.delete()
        
        return render(request, 'orders/success.html',{
            'order': order
        })
        
    total = sum(i.total_price() for i in items)
    
    return render(request, 'orders/checkout.html',{
        'items' : items,
        'total' : total
    })
    
def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    orders = Order.objects.filter(
        user = request.user
    ).order_by('-created_at')
    
    return render(request, 'orders/my_orders.html',{
        'orders':orders
    })