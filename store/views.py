from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Review
from orders.models import OrderItem, Order
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from store.forms import ReviewForm
from .models import Wishlist
from django.http import JsonResponse

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

    # ✅ Verified buyers list (string usernames)
    verified_users = list(
        OrderItem.objects.filter(
            product=product,
            order__status="Delivered"
        ).values_list('order__user', flat=True).distinct()
    )

    # ⭐ Average rating
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    if avg_rating:
        avg_rating = round(avg_rating, 1)
        avg_rating_int = int(avg_rating)
    else:
        avg_rating = 0
        avg_rating_int = 0

    form = ReviewForm()
    can_review = False

    # ⭐ rating breakdown
    rating_percent = {5:0, 4:0, 3:0, 2:0, 1:0}
    total_reviews = reviews.count()

    if total_reviews > 0:
        rating_percent[5] = int((reviews.filter(rating=5).count() / total_reviews) * 100)
        rating_percent[4] = int((reviews.filter(rating=4).count() / total_reviews) * 100)
        rating_percent[3] = int((reviews.filter(rating=3).count() / total_reviews) * 100)
        rating_percent[2] = int((reviews.filter(rating=2).count() / total_reviews) * 100)
        rating_percent[1] = int((reviews.filter(rating=1).count() / total_reviews) * 100)

    # ✅ check delivered purchase (FIXED)
    if request.user.is_authenticated:

        delivered_orders = Order.objects.filter(
            status="Delivered"
        )

        delivered_user_ids = delivered_orders.values_list('user', flat=True)

        delivered_products = OrderItem.objects.filter(
            order__in=delivered_orders,
            product=product
        )

        if delivered_products.exists() and request.user.id in delivered_user_ids:
            can_review = True
            
    # ✅ handle review submit
    if request.method == "POST":

        if not can_review:
            return redirect('product_detail', id=id)

        form = ReviewForm(request.POST)

        rating = request.POST.get('rating')
        comment = request.POST.get('review')

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        return redirect('product_detail', id=id)
    
    # ✅ RELATED PRODUCTS (same category)
    related_products = Product.objects.filter(
        Category=product.Category
    ).exclude(id=product.id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'can_review': can_review,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,
        'verified_users': verified_users,
        'rating_percent': rating_percent,
        'related_products': related_products
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

@login_required
def toggle_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        item.delete()
        return JsonResponse({'status': 'removed'})

    return JsonResponse({'status': 'added'})

@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'items': items})

