from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from src.models.clients import Client
from src.models.finance import Expense, Invoice
from src.models.projects import Project


def finance_dashboard(request):
    invoices = Invoice.objects.all().order_by("-date_issued")
    expenses = Expense.objects.all().order_by("-date")

    total_income = (
        Invoice.objects.filter(status="PAID").aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    total_expenses = Expense.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    net_profit = total_income - total_expenses

    pending_income = (
        Invoice.objects.exclude(status__in=["PAID", "CANCELLED", "DRAFT"]).aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )

    context = {
        "invoices": invoices[:5],
        "expenses": expenses[:5],
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "pending_income": pending_income,
    }
    return render(request, "finance/dashboard.html", context)


def invoice_list(request):
    invoices = Invoice.objects.all().order_by("-date_issued")
    return render(request, "finance/invoice_list.html", {"invoices": invoices})


def invoice_create(request):
    if request.method == "POST":
        client_id = request.POST.get("client")
        project_id = request.POST.get("project")
        invoice_number = request.POST.get("invoice_number")
        amount = request.POST.get("amount")
        date_issued = request.POST.get("date_issued")
        due_date = request.POST.get("due_date")
        status = request.POST.get("status")

        if client_id and invoice_number and amount:
            client = get_object_or_404(Client, id=client_id)
            project = get_object_or_404(Project, id=project_id) if project_id else None

            Invoice.objects.create(
                client=client,
                project=project,
                invoice_number=invoice_number,
                amount=amount,
                date_issued=date_issued,
                due_date=due_date,
                status=status,
            )
            return redirect("finance_dashboard")

    clients = Client.objects.all()
    projects = Project.objects.all()
    return render(
        request, "finance/invoice_form.html", {"clients": clients, "projects": projects}
    )


def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        client_id = request.POST.get("client")
        project_id = request.POST.get("project")
        invoice_number = request.POST.get("invoice_number")
        amount = request.POST.get("amount")
        date_issued = request.POST.get("date_issued")
        due_date = request.POST.get("due_date")
        status = request.POST.get("status")

        if client_id and invoice_number and amount:
            client = get_object_or_404(Client, id=client_id)
            project = get_object_or_404(Project, id=project_id) if project_id else None

            invoice.client = client
            invoice.project = project
            invoice.invoice_number = invoice_number
            invoice.amount = amount
            invoice.date_issued = date_issued
            invoice.due_date = due_date
            invoice.status = status
            invoice.save()
            return redirect("finance_dashboard")

    clients = Client.objects.all()
    projects = Project.objects.all()
    return render(
        request,
        "finance/invoice_form.html",
        {"invoice": invoice, "clients": clients, "projects": projects},
    )


@require_http_methods(["DELETE", "POST"])
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    if request.htmx:
        return HttpResponse("")
    return redirect("finance_dashboard")


def expense_list(request):
    expenses = Expense.objects.all().order_by("-date")
    return render(request, "finance/expense_list.html", {"expenses": expenses})


def expense_create(request):
    if request.method == "POST":
        description = request.POST.get("description")
        amount = request.POST.get("amount")
        date = request.POST.get("date")
        category = request.POST.get("category")

        if description and amount and date:
            Expense.objects.create(
                description=description, amount=amount, date=date, category=category
            )
            return redirect("finance_dashboard")

    return render(request, "finance/expense_form.html")


def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        description = request.POST.get("description")
        amount = request.POST.get("amount")
        date = request.POST.get("date")
        category = request.POST.get("category")

        if description and amount and date:
            expense.description = description
            expense.amount = amount
            expense.date = date
            expense.category = category
            expense.save()
            return redirect("finance_dashboard")

    return render(request, "finance/expense_form.html", {"expense": expense})


@require_http_methods(["DELETE", "POST"])
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    if request.htmx:
        return HttpResponse("")
    return redirect("finance_dashboard")
