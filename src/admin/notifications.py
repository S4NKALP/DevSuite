from django.contrib import admin
from src.admin.base import admin_site
from src.models.notifications import Notification

@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "subject", "status", "sent_at", "created_at")
    list_filter = ("status", "created_at", "sent_at")
    search_fields = ("recipient", "subject", "message")
    readonly_fields = ("created_at", "updated_at", "sent_at")
    date_hierarchy = "created_at"
