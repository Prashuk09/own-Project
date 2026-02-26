from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Review
from orders.models import OrderItem, Order
from django.contrib.auth.decorators import login_required
from orders.models import OrderItem


def home(request):

    query = request.GET.get('q')
    cat_id = request.GET.get('cat')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if cat_id:
        products = products.filter(category_id=cat_id)

    categories = Category.objects.all()

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, id):

    product = get_object_or_404(Product, id=id)
    
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            product=product,
            user=request.user
        ).first()


    has_ordered = False

    if request.user.is_authenticated:
        has_ordered = OrderItem.objects.filter(
            order__user=request.user,
            order__status="Delivered",
            product=product
        ).exists()

    reviews = Review.objects.filter(product=product)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'has_ordered': has_ordered,
        'reviews': reviews,
        'user_review': user_review,
    })
from .models import Review

@login_required
def add_review(request, id):

    product = get_object_or_404(Product, id=id)
    

    if request.method == "POST":

        rating = request.POST.get('rating')
        comment = request.POST.get('review')

        review, created = Review.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )

        # If exist update it
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()

    return redirect('product_detail', id=id)

