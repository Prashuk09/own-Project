from django.urls import path
from . import views

urlpatterns = [

    path("", views.notifications, name="notifications"),
    path('open/<int:id>/', views.notification_open, name='notification_open'),
    path("mark/<int:id>/", views.mark_single_read, name="mark_single_read"),
    path("mark-all/", views.mark_all_read, name="mark_all_read"),
    path("count/", views.unread_count, name="unread_count"),

]