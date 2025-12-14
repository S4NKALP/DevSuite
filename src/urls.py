"""generated with djinit"""

from django.urls import include, path

from src.admin.base import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", include("src.api.base.urls")),
    path("clients/", include("src.api.clients.urls")),
    path("projects/", include("src.api.projects.urls")),
]
