from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path("", views.productivity_dashboard, name="productivity_dashboard"),
    # Notes
    path("notes/", views.note_list, name="note_list"),
    path("notes/create/", views.note_create, name="note_create"),
    path("notes/<int:pk>/edit/", views.note_edit, name="note_edit"),
    path("notes/<int:pk>/delete/", views.note_delete, name="note_delete"),
    # Time entries
    path("time-entries/", views.timeentry_list, name="timeentry_list"),
    path("time-entries/create/", views.timeentry_create, name="timeentry_create"),
    path("time-entries/<int:pk>/edit/", views.timeentry_edit, name="timeentry_edit"),
    path(
        "time-entries/<int:pk>/delete/",
        views.timeentry_delete,
        name="timeentry_delete",
    ),
]
