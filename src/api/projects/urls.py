from django.urls import path

from src.api.projects import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("create/", views.project_create, name="project_create"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("<int:pk>/delete/", views.project_delete, name="project_delete"),
    path("<int:project_id>/tasks/create/", views.task_create, name="task_create"),
    path(
        "tasks/<int:task_id>/update/",
        views.task_update_status,
        name="task_update_status",
    ),
    path("tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:task_id>/detail/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),
]
