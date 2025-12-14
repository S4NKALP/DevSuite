from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from phonenumber_field.formfields import SplitPhoneNumberField

from src.models.clients import Client


class ClientForm(forms.ModelForm):
    phone = SplitPhoneNumberField(initial="+977")

    class Meta:
        model = Client
        fields = ["name", "email", "phone", "company_name", "address", "short_code"]
        widgets = {
            "short_code": forms.TextInput(attrs={"placeholder": "Optional"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].widget.widgets[0].attrs.update(
            {"class": "select select-bordered join-item"}
        )
        self.fields["phone"].widget.widgets[1].attrs.update(
            {"class": "input input-bordered join-item w-full"}
        )
        self.fields["short_code"].disabled = True


def client_list(request):
    clients = Client.objects.all()
    return render(request, "clients/client_list.html", {"clients": clients})


@require_http_methods(["GET", "POST"])
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:
                clients = Client.objects.all()
                return render(
                    request, "clients/partials/client_list.html", {"clients": clients}
                )
            return redirect("client_list")
    else:
        form = ClientForm()

    template = (
        "clients/partials/client_form.html"
        if request.htmx
        else "clients/client_form.html"
    )
    return render(request, template, {"form": form})


@require_http_methods(["GET", "POST"])
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            if request.htmx:
                clients = Client.objects.all()
                return render(
                    request, "clients/partials/client_list.html", {"clients": clients}
                )
            return redirect("client_list")
    else:
        form = ClientForm(instance=client)

    template = (
        "clients/partials/client_form.html"
        if request.htmx
        else "clients/client_form.html"
    )
    return render(request, template, {"form": form, "client": client})


@require_http_methods(["DELETE", "POST"])
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    if request.htmx:
        clients = Client.objects.all()
        return render(
            request, "clients/partials/client_list.html", {"clients": clients}
        )
    return redirect("client_list")
