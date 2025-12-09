"""generated with djinit"""

from django.urls import path

from src.admin.base import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
]
