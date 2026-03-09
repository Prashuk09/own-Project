from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from store.models import Product
from orders.models import Order, OrderItem
@login_required
def notifications(request):

    notes = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    for n in notes:
        n.product_name = None

        if n.link and "/cart/order/" in n.link:

            order_id = n.link.split("/cart/order/")[1].split("/")[0]

            order = Order.objects.get(id=order_id)

            item = OrderItem.objects.filter(order=order).first()

            if item:
                n.product_name = item.product.name

    return render(request,"notifications/notifications.html",{
        "notes":notes
    })
    
@login_required
def notification_open(request, id):

    notification = get_object_or_404(Notification, id=id, user=request.user)

    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)

    return redirect("/")

@login_required
def mark_single_read(request, id):

    n = Notification.objects.get(id=id, user=request.user)

    n.is_read = True
    n.save()

    return JsonResponse({"status":"success"})


@login_required
def mark_all_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"status":"success"})


@login_required
def unread_count(request):

    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({"count":count})