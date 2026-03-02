from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [

    path('profile/', views.profile, name='profile'),

    path('add-address/', views.add_address, name='add_address'),

    path('edit-address/<int:id>/', views.edit_address, name='edit_address'),

    path('delete-address/<int:id>/', views.delete_address, name='delete_address'),

]