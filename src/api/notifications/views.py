from django.shortcuts import get_object_or_404, render

from src.models.notifications import Notification


def notifications_dashboard(request):
    recent_notifications = Notification.objects.all()[:10]
    pending_count = Notification.objects.filter(status="PENDING").count()
    failed_count = Notification.objects.filter(status="FAILED").count()
    sent_count = Notification.objects.filter(status="SENT").count()

    return render(
        request,
        "notifications/dashboard.html",
        {
            "recent_notifications": recent_notifications,
            "pending_count": pending_count,
            "failed_count": failed_count,
            "sent_count": sent_count,
        },
    )


def notification_list(request):
    notifications = Notification.objects.all()
    return render(
        request,
        "notifications/notification_list.html",
        {"notifications": notifications},
    )


def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    return render(
        request,
        "notifications/notification_detail.html",
        {"notification": notification},
    )
