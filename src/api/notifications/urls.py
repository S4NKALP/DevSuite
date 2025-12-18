from django.urls import path

from . import views

urlpatterns = [
    path("", views.notifications_dashboard, name="notifications_dashboard"),
    path("list/", views.notification_list, name="notification_list"),
    path("<int:pk>/detail/", views.notification_detail, name="notification_detail"),
]


