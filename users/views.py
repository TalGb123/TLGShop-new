from datetime import date
import http.client
from urllib.parse import urlencode

import orjson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import HttpResponse, redirect, render

from shop.models import Customer, User

from .forms import UserRegisterForm

# Create your views here.


def register(req: HttpRequest):
    default = lambda: render(req, "register.html", {"form": form})
    if req.method == "POST":
        form = UserRegisterForm(req.POST)
        if not form.is_valid():
            messages.success(req, f"User creation failed you bastard")
            return default()
        elif not email_vrf(req.POST["email"]):
            messages.success(req, f"Thou's email exists not")
            return default()
        else:
            account = form.save()
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            id = form.cleaned_data["id"]

            Customer(
                account=account,
                person_id=id,
                first_name=first_name,
                last_name=last_name,
                email=email,
            ).save()

            messages.error(
                req, f"Your account has been created! You are now able to log in"
            )
            return redirect("login")
    else:
        form = UserRegisterForm()
    return default()


def email_vrf(chosen_mail):
    conn = http.client.HTTPConnection("api.eva.pingutil.com")
    payload = ""
    conn.request("GET", f"/email?{urlencode({ 'email': chosen_mail })}", payload)
    res = conn.getresponse()
    return orjson.loads(res.read().decode())["data"]["deliverable"]


@login_required
def profile(request: HttpRequest):
    context = {"worker": is_worker(request)}
    return render(request, "profile.html", context)


def profile_show_data(request: HttpRequest):
    if request.method == "GET":
        try:
            customer = Customer.objects.get(account=request.user)

            data = {
                "person_id": customer.person_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "birth_date": customer.birth_date,
                "city": customer.city,
                "street": customer.street,
                "building_number": customer.building_number,
                "apartment_number": customer.apartment_number,
                "cellphone_number": customer.cellphone_number,
            }
            return JsonResponse(data)
        except Customer.DoesNotExist:
            return JsonResponse(
                {
                    "person_id": "",
                    "first_name": "",
                    "last_name": "",
                    "birth_date": "",
                    "city": "",
                    "street": "",
                    "building_number": "",
                    "apartment_number": "",
                    "cellphone_number": "",
                },
                status=404,
            )
    else:
        return JsonResponse({"error": "bad method"}, status=405)


def is_worker(request):
    worker = request.user.is_authenticated and (
        request.user.groups.filter(name="Worker").exists()
        or request.user.groups.filter(name="Admin").exists()
    )
    return worker


def profile_update(request: HttpRequest):
    person_id = request.POST.get("person_id")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    birth_date = request.POST.get("birth_date")
    city = request.POST.get("city")
    street = request.POST.get("street")
    building_number = request.POST.get("building_number")
    apartment_number = request.POST.get("apartment_number")
    cellphone_number = request.POST.get("cellphone_number")

    customer = Customer.objects.get(account=request.user)

    if person_id is not None:
        customer.person_id = person_id
    if first_name is not None:
        customer.first_name = first_name
    if last_name is not None:
        customer.last_name = last_name
    if birth_date is not None:
        customer.birth_date = date.fromisoformat(birth_date)
    if city is not None:
        customer.city = city
    if street is not None:
        customer.street = street
    if building_number is not None:
        customer.building_number = (
            int(building_number) if building_number != "" else None
        )
    if apartment_number is not None:
        customer.apartment_number = (
            int(apartment_number) if apartment_number != "" else None
        )
    if cellphone_number is not None:
        customer.cellphone_number = cellphone_number if cellphone_number != "" else None

    customer.save()

    return HttpResponseRedirect("/profile/")
