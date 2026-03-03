from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [

    # AUTH
    path('signup/', views.signup, name='signup'),

    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),

    # PROFILE
    path('profile/', views.profile, name='profile'),

    # ADDRESS
    path('add-address/', views.add_address, name='add_address'),
    path('edit-address/<int:id>/', views.edit_address, name='edit_address'),
    path('delete-address/<int:id>/', views.delete_address, name='delete_address'),
]