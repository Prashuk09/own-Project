from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from accounts.models import Address
from notifications.utils import create_notification

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity
    
class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    # 🔔 Notification Trigger
    def save(self, *args, **kwargs):

        # check old status
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)

            if old_order.status != self.status:

                if self.status == "Shipped":
                    create_notification(
                        self.user,
                        "Order Shipped",
                        f"Your order #{self.id} has been shipped",
                        f"/cart/order/{self.id}/"
                    )

                elif self.status == "Delivered":
                    create_notification(
                        self.user,
                        "Order Delivered",
                        f"Your order #{self.id} has been delivered",
                        f"/cart/order/{self.id}/"
                    )

                elif self.status == "Cancelled":
                    create_notification(
                        self.user,
                        "Order Cancelled",
                        f"Your order #{self.id} has been cancelled",
                        f"/cart/order/{self.id}/"
                    )

        super().save(*args, **kwargs)
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    price = models.IntegerField()
    quantity = models.IntegerField()

    def get_total(self):
        return self.price * self.quantity

class CancelRequest(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    reason = models.TextField()

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancel Request - Order {self.order.id}"

    # 🔥 IMPORTANT FIXED SAVE METHOD
    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.is_approved:

            self.order.status = "Cancelled"
            self.order.save()

           
    


