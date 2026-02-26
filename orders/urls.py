from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('inc/<int:item_id>/', views.increase_qty, name='inc_qty'),
    path('dec/<int:item_id>/', views.decrease_qty, name='dec_qty'),
    path('remove/<int:item_id>/', views.remove_item, name='remove_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
