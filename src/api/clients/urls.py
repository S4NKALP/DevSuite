from django.urls import path

from src.api.clients import views

urlpatterns = [
    path("", views.client_list, name="client_list"),
    path("create/", views.client_create, name="client_create"),
    path("<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("<int:pk>/delete/", views.client_delete, name="client_delete"),
]
