import http.client
from urllib.parse import urlencode

import orjson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import HttpResponse, redirect, render

from shop.models import Customer

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

            Customer(account=account).save()

            messages.success(
                req, f"Your account has been created! You are now able to log in"
            )
            return redirect("login")
    else:
        form = UserRegisterForm()
    return default()


def email_vrf(chosen_mail):
    conn = http.client.HTTPConnection("api.eva.pingutil.com")
    payload = ""
    headers = {}
    conn.request(
        "GET", f"/email?{urlencode({ 'email': chosen_mail })}", payload, headers
    )
    res = conn.getresponse()
    return orjson.loads(res.read().decode())["data"]["deliverable"]


@login_required
def profile(request):
    return render(request, "profile.html")
