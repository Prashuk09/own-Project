from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Address
from .forms import SignupForm, AddressForm
from orders.models import Order


# ✅ SIGNUP
def signup(request):

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"]
            )

            login(request, user)
            return redirect('/')

    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


# ✅ PROFILE PAGE (ONLY ONE VIEW)
@login_required
def profile(request):

    addresses = Address.objects.filter(user=request.user)

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-id')[:5]

    return render(request, 'accounts/profile.html', {
        'addresses': addresses,
        'orders': orders
    })


# ✅ ADD ADDRESS
@login_required
def add_address(request):

    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            # default address logic
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)

            address.save()

            messages.success(request, "Address added successfully")

            return redirect('accounts:profile')   # ✅ FIX

    else:
        form = AddressForm()

    return render(request, 'accounts/add_address.html', {'form': form})
@login_required
def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            updated_address = form.save(commit=False)

            if updated_address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)

            updated_address.save()
            messages.success(request, "Address updated")
            return redirect('accounts:profile')

    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/add_address.html', {'form': form})


@login_required
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted")
    return redirect('accounts:profile')