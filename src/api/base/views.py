from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from src.models.clients import Client
from src.models.finance import Expense, Invoice
from src.models.projects import Project, Task
from src.models.services import Service


def is_superuser(user):
    return user.is_superuser


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            messages.error(
                request,
                "Invalid credentials or insufficient permissions. Superuser access required.",
            )
    return render(request, "base/login.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect("login")


@login_required(login_url="login")
@user_passes_test(is_superuser, login_url="login")
def dashboard(request):
    # Date ranges
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    # Core metrics
    total_clients = Client.objects.count()
    active_projects = Project.objects.filter(status="In_PROGRESS").count()
    pending_tasks = Task.objects.filter(status="TODO").count()

    # Financial metrics
    total_income = (
        Invoice.objects.filter(status="PAID").aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    pending_income = (
        Invoice.objects.filter(status="SENT").aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    monthly_expenses = (
        Expense.objects.filter(date__gte=month_ago).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )
    overdue_invoices = Invoice.objects.filter(status="OVERDUE").count()

    # Recent Activity
    recent_projects = Project.objects.select_related("client").order_by("-updated_at")[
        :5
    ]
    recent_tasks = Task.objects.select_related("project").order_by("-updated_at")[:5]
    upcoming_deadlines = Project.objects.filter(
        deadline__gte=today, deadline__lte=today + timedelta(days=7)
    ).order_by("deadline")[:5]

    # Services expiring soon
    expiring_services = Service.objects.filter(
        expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30)
    ).order_by("expiry_date")[:5]

    context = {
        "total_clients": total_clients,
        "active_projects": active_projects,
        "pending_tasks": pending_tasks,
        "total_income": total_income,
        "pending_income": pending_income,
        "monthly_expenses": monthly_expenses,
        "overdue_invoices": overdue_invoices,
        "recent_projects": recent_projects,
        "recent_tasks": recent_tasks,
        "upcoming_deadlines": upcoming_deadlines,
        "expiring_services": expiring_services,
    }
    return render(request, "base/dashboard.html", context)
