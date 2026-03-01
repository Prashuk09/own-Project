from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Review
from orders.models import OrderItem, Order
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from store.forms import ReviewForm


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

    reviews = Review.objects.filter(product=product)

    # ✅ Verified buyers list
    verified_users = OrderItem.objects.filter(
        product=product,
        order__status="Delivered"
    ).values_list('order__user', flat=True)

    # ⭐ Average rating
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    if avg_rating:
        avg_rating = round(avg_rating, 1)
        avg_rating_int = int(avg_rating)   # ⭐ star fill fix
    else:
        avg_rating = 0
        avg_rating_int = 0

    form = ReviewForm()
    can_review = False

    # ✅ check delivered purchase
    if request.user.is_authenticated:
        delivered_orders = Order.objects.filter(
            user=request.user,
            status="Delivered"
        )

        if OrderItem.objects.filter(
            order__in=delivered_orders,
            product=product
        ).exists():
            can_review = True

    # ✅ handle review submit
    if request.method == "POST":

        if not can_review:
            return redirect('product_detail', id=id)

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            return redirect('product_detail', id=id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'can_review': can_review,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,   # ⭐ IMPORTANT
        'verified_users': verified_users
    })


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

        # update existing review
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()

    return redirect('product_detail', id=id)