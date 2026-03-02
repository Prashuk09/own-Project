from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    address_line = models.TextField()
    landmark = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name