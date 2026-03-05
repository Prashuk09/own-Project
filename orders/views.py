from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem, CancelRequest
from accounts.models import Address
from store.models import Product

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# ---------------- CART ---------------- #

def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return cart


def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'})

    product = get_object_or_404(Product, id=product_id)

    cart = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # OUT OF STOCK
    if product.stock == 0:
        return JsonResponse({
            "status": "out_of_stock"
        })

    # FIRST TIME ADD
    if created:
        item.quantity = 1

    else:

        # MAX STOCK REACHED
        if item.quantity >= product.stock:

            return JsonResponse({
                "status": "max_stock",
                "stock": product.stock
            })

        item.quantity += 1

    item.save()

    return JsonResponse({
        "status": "success",
        "qty": item.quantity
    })

@require_POST
def increase_qty(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)
    product = item.product

    # STOCK LIMIT
    if item.quantity >= product.stock:
        return JsonResponse({
            "status": "max_stock",
            "stock": product.stock
        })

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

    return JsonResponse({"status": "removed"})


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


# ---------------- CHECKOUT ---------------- #

@login_required
def checkout(request):

    cart = get_cart(request)
    items = cart.cartitem_set.all()

    if not items:
        return redirect('view_cart')

    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    total = sum(item.product.price * item.quantity for item in items)

    # address required
    if not addresses.exists():
        messages.error(request, "Please add a delivery address first.")
        return redirect("accounts:add_address")

    if request.method == "POST":

        address_id = request.POST.get('address')

        if address_id:
            selected_address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            selected_address = default_address or addresses.first()

        # STOCK CHECK FIRST
        for item in items:
            product = item.product
            if item.quantity > product.stock:
                messages.error(request, f"{product.name} is out of stock.")
                return redirect("view_cart")

        # ORDER CREATE
        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            total_amount=total
        )

        # CREATE ORDER ITEMS + REDUCE STOCK
        for item in items:

            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            # reduce stock AFTER order
            product.stock -= item.quantity
            product.save()

        # clear cart
        items.delete()

        return redirect('my_orders')

    return render(request, 'orders/checkout.html', {
        'items': items,
        'default_address': default_address,
        'addresses': addresses,
        'total': total
    })

@login_required
def order_detail(request, id):

    order = get_object_or_404(Order, id=id, user=request.user)

    cancel_request = CancelRequest.objects.filter(order=order).first()

    items = OrderItem.objects.filter(order=order)

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items,
        "cancel_request": cancel_request
    })


# ---------------- CANCEL REQUEST ---------------- #

@login_required
def cancel_request(request, id):

    order = get_object_or_404(Order, id=id, user=request.user)

    if CancelRequest.objects.filter(order=order).exists():
        messages.warning(request, "Cancellation already requested.")
        return redirect('order_detail', id=order.id)

    if request.method == "POST":

        reason = request.POST.get("reason")

        CancelRequest.objects.create(
            order=order,
            user=request.user,
            reason=reason
        )

        messages.success(request, "Cancellation request submitted.")

        return redirect('order_detail', id=order.id)

    return render(request, "orders/cancel_request.html", {
        "order": order
    })


# ---------------- DIRECT CANCEL ---------------- #

@login_required
def cancel_order(request, id):

    order = get_object_or_404(Order, id=id, user=request.user)

    order.status = "Cancelled"
    order.save()

    messages.success(request, "Order cancelled successfully.")

    return redirect('order_detail', id=order.id)


# ---------------- INVOICE ---------------- #

def download_invoice(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Invoice #{order.id}", styles['Heading1']))
    elements.append(Spacer(1, 20))

    address = order.address

    elements.append(Paragraph(f"Customer: {order.user}", styles['Normal']))

    if address:
        elements.append(Paragraph(f"Name: {address.full_name}", styles['Normal']))
        elements.append(Paragraph(f"Phone: {address.phone}", styles['Normal']))
        elements.append(Paragraph(
            f"Address: {address.address_line}, {address.city}, {address.state} - {address.pincode}",
            styles['Normal']
        ))
    else:
        elements.append(Paragraph("Address: N/A", styles['Normal']))

    elements.append(Spacer(1, 20))

    data = [['Product', 'Qty', 'Price']]

    for item in items:
        data.append([
            item.product.name,
            item.quantity,
            f"₹ {item.product.price}"
        ])

    table = Table(data, colWidths=[220, 80, 100])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    elements.append(Paragraph("PJKART Pvt Ltd", styles['Heading2']))
    elements.append(Paragraph("Bharuch, Gujarat", styles['Normal']))
    elements.append(Paragraph("Phone: +91 XXXXX XXXXX", styles['Normal']))

    elements.append(Spacer(1, 25))

    elements.append(Paragraph(f"Total Amount: ₹ {order.total_amount}", styles['Heading2']))

    doc.build(elements)

    return response

# BUY NOW VIEW
@login_required
def buy_now(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if product.stock < 1:
        messages.error(request, "Product out of stock")
        return redirect("product_detail", product_id)

    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    items = [{
        "product": product,
        "quantity": 1,
        "total_price": product.price
    }]

    total = product.price

    return render(request, "orders/checkout.html", {
        "items": items,
        "buy_now": True,
        "product": product,
        "total": total,
        "addresses": addresses,
        "default_address": default_address
    })

# ---------------- ORDERS ---------------- #

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'orders/my_orders.html', {
        'orders': orders
    })