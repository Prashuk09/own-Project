from django.contrib import admin
from .models import Category, Product, Review, ProductImage


# Category register
admin.site.register(Category)


# Review register
admin.site.register(Review)


# Product Image Inline (Gallery)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


# Product Admin with gallery images
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


# Register Product with ProductAdmin
admin.site.register(Product, ProductAdmin)


# Register ProductImage separately (optional but useful)
admin.site.register(ProductImage)