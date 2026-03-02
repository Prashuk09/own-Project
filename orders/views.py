from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from django.contrib.auth.decorators import login_required


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

from accounts.models import Address

@login_required
def checkout(request):

    cart = Cart.objects.get(user=request.user)
    items = cart.cartitem_set.all()

    if not items:
        return redirect('view_cart')

    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    # ✅ calculate total
    total = sum(item.product.price * item.quantity for item in items)

    if request.method == "POST":

        address_id = request.POST.get('address')

        if address_id:
            selected_address = Address.objects.get(id=address_id, user=request.user)
        else:
            selected_address = default_address

        order = Order.objects.create(
            user=request.user,   # ✅ FIXED
            address=selected_address,
            total_amount=total   # ✅ FIXED
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        items.delete()

        return redirect('my_orders')

    return render(request, 'orders/checkout.html', {
        'items': items,
        'default_address': default_address,
        'addresses': addresses,
        'total': total
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

def download_invoice(request, order_id):

    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    # 🧾 Title
    elements.append(Paragraph(f"Invoice #{order.id}", styles['Heading1']))
    elements.append(Spacer(1, 20))

    # ✅ Customer Info
    address = order.address   # FK Address object

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

    # 🛒 Table data
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

    # 🏢 Company Info
    elements.append(Paragraph("PJKART Pvt Ltd", styles['Heading2']))
    elements.append(Paragraph("Bharuch, Gujarat", styles['Normal']))
    elements.append(Paragraph("Phone: +91 XXXXX XXXXX", styles['Normal']))

    elements.append(Spacer(1, 25))

    # 💰 Total
    elements.append(Paragraph(f"Total Amount: ₹ {order.total_amount}", styles['Heading2']))

    doc.build(elements)

    return response