from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User

from .forms import SignupForm


def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data  # cleaned_data

            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"]
            )

            login(request, user)

            return redirect('/')

    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {
        'form': form
    })

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'accounts/profile.html')