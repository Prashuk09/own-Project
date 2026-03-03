from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, CancelRequest

# CART MODELS (Simple Register)

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)

# ORDER ADMIN (OLD FUNCTION SAFE)

class OrderAdmin(admin.ModelAdmin):

    # Table columns
    list_display = ('id', 'user', 'status', 'total_amount')

    # User clickable 
    list_display_links = ('user',)

    # Filter right side
    list_filter = ('status',)

    # Search bar
    search_fields = ('user__username',)

    # hidden for cancelled orders
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status="Cancelled")


admin.site.register(Order, OrderAdmin)
# CANCEL REQUEST ADMIN

@admin.register(CancelRequest)
class CancelRequestAdmin(admin.ModelAdmin):

    list_display = ('order', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved',)

    actions = ['approve_cancellation']

    def approve_cancellation(self, request, queryset):
        for obj in queryset:
            obj.is_approved = True
            obj.save()

            # Order status update
            obj.order.status = "Cancelled"
            obj.order.save()

    approve_cancellation.short_description = "Approve selected cancel requests"