from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from accounts.models import Address

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
    user = models.CharField(max_length=200)

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_amount = models.IntegerField()

    status = models.CharField(max_length=20, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)
    
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    price = models.IntegerField()
    quantity = models.IntegerField()

    def get_total(self):
        return self.price * self.quantity