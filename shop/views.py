import random
from datetime import date, datetime

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.detail import DetailView

from .models import *

# Create your views here.


# home functions
def view_home(request: HttpRequest):

    context = {"title": "Home", "worker": is_worker(request)}
    return render(request, "shop/home.html", context)


# product functions
def view_products(request: HttpRequest):
    # computers = list(Computer.objects.all())
    components = list(Component.objects.all())
    data = components  # + computers
    context = {
        "products": data,
        "title": "Products",
        "mf_list": Product.mf_list,
        "category_list": Component.category_list,
        "worker": is_worker(request),
    }
    return render(request, "shop/products.html", context)


def filter_products(request: HttpRequest):
    selected_manufacturers = request.GET.getlist("manufacturer")
    selected_categories = request.GET.getlist("category")

    data = Component.objects.all()

    print(selected_manufacturers)
    if selected_manufacturers:
        data = Component.objects.filter(manufacturer__in=selected_manufacturers)

    print(data)

    if selected_categories:
        data = data.filter(category__in=selected_categories)

    context = {
        "products": list(data),
        "title": "Products",
        "worker": is_worker(request),
    }

    return render(request, "shop/product_list.html", context)


# def view_customers_table(request: HttpRequest):
#     data = Customer.objects.all()
#     context = {"customers": data, "title": "Customers"}
#     return render(request, "shop/customers_table.html", context)


class ProductDetailView(DetailView):
    model = Product


def create_component(request: HttpRequest):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        name = request.POST.get("name")
        price = request.POST.get("price")
        manufacturer = request.POST.get("manufacturer")
        stock = request.POST.get("stock")
        mf_page = request.POST.get("mf_page")
        image = request.FILES.get("image")
        category = request.POST.get("category")

        if not (
            name and price and manufacturer and mf_page and category and product_id
        ):
            return HttpResponse("Missing required fields")

        if image is None:
            image = "default.png"

        stock = stock is not None

        new_component = Component(
            product_id=product_id,
            name=name,
            price=price,
            manufacturer=manufacturer,
            stock=stock,
            mf_page=mf_page,
            image=image,
            category=category,
        )
        new_component.save()

        return HttpResponseRedirect("/products/")
    else:
        return HttpResponse(request)


def search_product(request: HttpRequest):
    if request.method == "GET":
        product_id = request.GET.get("product_id")
        try:
            computer = Computer.objects.get(product_id=product_id)

            data = {
                "product_id": computer.product_id,
                "name": computer.name,
                "price": computer.price,
                "manufacturer": computer.manufacturer,
                "stock": computer.stock,
                "mf_page": computer.mf_page,
                "image": computer.image.url[22:],
                "components": [{"name": comp.name} for comp in computer.components],
            }
            return JsonResponse(data)
        except Computer.DoesNotExist:
            pass

        try:
            component = Component.objects.get(product_id=product_id)

            data = {
                "product_id": component.product_id,
                "name": component.name,
                "price": component.price,
                "manufacturer": component.manufacturer,
                "stock": component.stock,
                "mf_page": component.mf_page,
                "image": component.image.url[22:],
                "category": component.category,
            }
            return JsonResponse(data)
        except Component.DoesNotExist:
            pass
    return JsonResponse({"error": "bad method"}, status=405)


def delete_product(request: HttpRequest):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        if product_id is None:
            return JsonResponse({"message": "Product not found"}, status=404)
        try:
            Computer.objects.filter(product_id=product_id).delete()
            # return HttpResponseRedirect("/products/")
        except:
            pass

        try:
            Component.objects.filter(product_id=product_id).delete()
            # return HttpResponseRedirect("/products/")
        except:
            pass
    return JsonResponse({"message": "Invalid request"}, status=400)


def update_product(request: HttpRequest):
    product_id = request.POST.get("product_id")
    name = request.POST.get("name")
    price = request.POST.get("price")
    manufacturer = request.POST.get("manufacturer")
    stock = request.POST.get("stock")
    mf_page = request.POST.get("mf_page")
    image = request.FILES.get("image")
    category = request.POST.get("category")

    try:
        component = Component.objects.get(product_id=product_id)

        if name is not None:
            component.name = name
        if price is not None:
            component.price = int(price)
        if manufacturer is not None:
            component.manufacturer = manufacturer
        stock = stock is not None
        if mf_page is not None:
            component.mf_page = mf_page
        # if image is not None:
        #     computer.image = image
        if category is not None:
            component.category = category

        component.save()
        return HttpResponseRedirect("/products/")
    except Component.DoesNotExist:
        pass

    try:
        computer = Computer.objects.get(product_id=product_id)

        if name is not None:
            computer.name = name
        if price is not None:
            computer.price = int(price)
        if manufacturer is not None:
            computer.manufacturer = manufacturer
        stock = stock is not None
        if mf_page is not None:
            computer.mf_page = mf_page
        # if image is not None:
        #     computer.image = image
        # if components is not None:
        #     computer.components = [{"name": comp.name} for comp in computer.components]

        computer.save()
        return HttpResponseRedirect("/products/")
    except Component.DoesNotExist:
        pass

    return HttpResponseRedirect("/products/")


# customer functions


def view_customers(request: HttpRequest):
    data = Customer.objects.all()
    context = {"customers": data, "title": "Customers", "worker": is_worker(request)}
    return render(request, "shop/customers.html", context)


def view_customers_table(request: HttpRequest):
    data = Customer.objects.all()
    context = {"customers": data, "title": "Customers"}
    return render(request, "shop/customers_table.html", context)


def create_customer(request: HttpRequest):
    if request.method == "POST":
        person_id = request.POST.get("person_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        birth_date = request.POST.get("birth_date")
        city = request.POST.get("city")
        street = request.POST.get("street")
        building_number = request.POST.get("building_number")
        apartment_number = request.POST.get("apartment_number")
        cellphone_number = request.POST.get("cellphone_number")
        account = request.POST.get("username")
        membership = request.POST.get("membership")
        ms_points = request.POST.get("ms_points")

        if person_id is None:
            return HttpResponse(request)

        if first_name is None:
            return HttpResponse(request)

        if last_name is None:
            return HttpResponse(request)

        if city is None:
            city = ""

        if street is None:
            street = ""

        if building_number is None:
            building_number = ""

        if apartment_number is None:
            apartment_number = ""

        if cellphone_number is None:
            cellphone_number = ""

        if account is None:
            return HttpResponse(request)

        membership = membership is not None

        if (ms_points is None) or (membership == "false"):
            ms_points = 0

        new_customer = Customer(
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            city=city,
            street=street,
            building_number=building_number,
            apartment_number=apartment_number,
            cellphone_number=cellphone_number,
            account=User.objects.get(username=account),
            membership=membership,
            ms_points=ms_points,
        )
        new_customer.save()

        return HttpResponseRedirect("/customers/")
    else:
        return HttpResponse(request)


def search_customer(request: HttpRequest):
    if request.method == "GET":
        person_id = request.GET.get("person_id")
        try:
            customer = Customer.objects.get(person_id=person_id)

            data = {
                "person_id": customer.person_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "birth_date": customer.birth_date,
                "city": customer.city,
                "street": customer.street,
                "building_number": customer.building_number,
                "apartment_number": customer.apartment_number,
                "cellphone_number": customer.cellphone_number,
                "account": customer.account.username,
                "membership": customer.membership,
                "ms_points": customer.ms_points,
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
                    "membership": "",
                    "ms_points": "",
                },
                status=404,
            )
    else:
        return JsonResponse({"error": "bad method"}, status=405)


def delete_customer(request: HttpRequest):
    if request.method == "POST":
        person_id = request.POST.get("person_id")
        if person_id is None:
            return JsonResponse({"message": "Customer not found"}, status=404)
        try:
            Customer.objects.filter(person_id=person_id).delete()
            return HttpResponseRedirect("/customers/")
        except:
            return JsonResponse({"message": "Customer not found"}, status=404)
    return JsonResponse({"message": "Invalid request"}, status=400)


def update_customer(request: HttpRequest):
    person_id = request.POST.get("person_id")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    birth_date = request.POST.get("birth_date")
    city = request.POST.get("city")
    street = request.POST.get("street")
    building_number = request.POST.get("building_number")
    apartment_number = request.POST.get("apartment_number")
    cellphone_number = request.POST.get("cellphone_number")
    account = request.POST.get("account_id")
    membership = request.POST.get("membership")
    ms_points = request.POST.get("ms_points")

    customer = Customer.objects.get(person_id=person_id)

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
        customer.building_number = int(building_number)
    if apartment_number is not None:
        customer.apartment_number = int(apartment_number)
    if cellphone_number is not None:
        customer.cellphone_number = cellphone_number
    if account is not None:
        customer.account = User.objects.get(pk=int(account))
    customer.membership = membership is not None
    if ms_points is not None:
        customer.ms_points = int(ms_points)

    customer.save()

    return HttpResponseRedirect("/customers/")


# worker functions


def view_workers(request: HttpRequest):
    data = Worker.objects.all()  # Fetch all rows from MyTable
    context = {
        "workers": data,
        "title": "Workers",
        "branches": Worker.branches,
        "worker": is_worker(request),
    }
    return render(request, "shop/workers.html", context)


def create_worker(request: HttpRequest):
    if request.method == "POST":
        person_id = request.POST.get("person_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        birth_date = request.POST.get("birth_date")
        city = request.POST.get("city")
        street = request.POST.get("street")
        building_number = request.POST.get("building_number")
        apartment_number = request.POST.get("apartment_number")
        cellphone_number = request.POST.get("cellphone_number")
        account = request.POST.get("account_id")
        work_branch = request.POST.get("work_branch")
        job_title = request.POST.get("job_title")
        workstart_date = request.POST.get("workstart_date")

        if person_id is None:
            return HttpResponse(request)

        if first_name is None:
            return HttpResponse(request)

        if last_name is None:
            return HttpResponse(request)

        if birth_date is None:
            return HttpResponse(request)

        if city is None:
            return HttpResponse(request)

        if street is None:
            street = ""

        if building_number is None:
            building_number = ""

        if apartment_number is None:
            apartment_number = ""

        if cellphone_number is None:
            return HttpResponse(request)

        if account is None:
            return HttpResponse(request)

        if work_branch is None:
            work_branch = False

        if job_title is None:
            job_title = ""

        if workstart_date is None:
            now = datetime.now()

        new_worker = Worker(
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            city=city,
            street=street,
            building_number=building_number,
            apartment_number=apartment_number,
            cellphone_number=cellphone_number,
            account=User.objects.get(id=int(account)),
            work_branch=work_branch,
            job_title=job_title,
            workstart_date=now,
        )
        new_worker.save()

        return HttpResponseRedirect("/workers/")
    else:
        return HttpResponse(request)


def search_worker(request: HttpRequest):
    if request.method == "GET":
        person_id = request.GET.get("person_id")
        try:
            worker = Worker.objects.get(person_id=person_id)
            data = {
                "person_id": worker.person_id,
                "first_name": worker.first_name,
                "last_name": worker.last_name,
                "birth_date": worker.birth_date,
                "city": worker.city,
                "street": worker.street,
                "building_number": worker.building_number,
                "apartment_number": worker.apartment_number,
                "cellphone_number": worker.cellphone_number,
                "account": worker.account.pk,
                "work_branch": worker.work_branch,
                "job_title": worker.job_title,
                "workstart_date": worker.workstart_date,
            }
            return JsonResponse(data)
        except Worker.DoesNotExist:
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
                    "work_branch": "",
                    "job_title": "",
                    "workstart_date": "",
                },
                status=404,
            )
    else:
        return JsonResponse({"error": "bad method"}, status=405)


def delete_worker(request: HttpRequest):
    if request.method == "POST":
        person_id = request.POST.get("person_id")
        if person_id is None:
            return JsonResponse({"message": "Worker not found"}, status=404)
        try:
            Worker.objects.filter(person_id=person_id).delete()
            return HttpResponseRedirect("/shop/workers/")
        except:
            return JsonResponse({"message": "Worker not found"}, status=404)
    return JsonResponse({"message": "Invalid request"}, status=400)


def update_worker(request: HttpRequest):
    person_id = request.POST.get("person_id")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    birth_date = request.POST.get("birth_date")
    city = request.POST.get("city")
    street = request.POST.get("street")
    building_number = request.POST.get("building_number")
    apartment_number = request.POST.get("apartment_number")
    cellphone_number = request.POST.get("cellphone_number")
    account = request.POST.get("account_id")
    work_branch = request.POST.get("work_branch")
    job_title = request.POST.get("job_title")
    workstart_date = request.POST.get("workstart_date")

    worker = Worker.objects.get(person_id=person_id)

    if first_name is not None:
        worker.first_name = first_name
    if last_name is not None:
        worker.last_name = last_name
    if birth_date is not None:
        worker.birth_date = date.fromisoformat(birth_date)
    if city is not None:
        worker.city = city
    if street is not None:
        worker.street = street
    if building_number is not None:
        worker.building_number = int(building_number)
    if apartment_number is not None:
        worker.apartment_number = int(apartment_number)
    if cellphone_number is not None:
        worker.cellphone_number = cellphone_number
    if account is not None:
        worker.account = User.objects.get(pk=int(account))
    if work_branch is not None:
        worker.work_branch = work_branch
    if job_title is not None:
        worker.job_title = job_title
    if workstart_date is not None:
        worker.workstart_date = date.fromisoformat(workstart_date)

    worker.save()

    return HttpResponseRedirect("/workers/")


# spec builder functions
def view_builder(request):
    context = {
        "title": "Builder",
        "categories": [
            ("Processor", "cpu.svg"),
            ("Cooler", "cooling.svg"),
            ("Motherboard", "mobo.svg"),
            ("Memory", "memory.svg"),
            ("Power Supply", "psu.svg"),
            ("Storage", "storage.svg"),
            ("Case", "case.svg"),
            ("Graphics Card", "gpu.svg"),
            ("Keyboard", "kbm.svg"),
            ("Mouse", "kbm.svg"),
            ("Monitor", "monitor.svg"),
        ],
        "worker": is_worker(request),
    }
    return render(request, "shop/builder.html", context)


def category_list(request: HttpRequest):
    if request.method == "GET":
        category = request.GET.get("category")
        print("Category:", category)
        # Filter products by category
        products = Component.objects.filter(category=category)
        # Serialize products using Django's serializer
        serialized_products = [
            {
                "pk": product.pk,
                "fields": {
                    "product_id": product.product_id,
                    "category": product.category,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image.url,  # Convert ImageField to string
                    "mf_page": product.mf_page,
                    # Add other fields as needed
                },
            }
            for product in products
        ]
        return JsonResponse({"products": serialized_products})
    else:
        return JsonResponse({"error": "Invalid request method"})


def view_builder_table(request: HttpRequest):
    context = context = {
        "title": "Builder",
        "categories": [
            ("Processor", "cpu.svg"),
            ("Cooler", "cooling.svg"),
            ("Motherboard", "mobo.svg"),
            ("Memory", "memory.svg"),
            ("Power Supply", "psu.svg"),
            ("Storage", "storage.svg"),
            ("Case", "case.svg"),
            ("Graphics Card", "gpu.svg"),
            ("Keyboard", "kbm.svg"),
            ("Mouse", "kbm.svg"),
            ("Monitor", "monitor.svg"),
        ],
    }
    return render(request, "shop/builder_table.html", context)


def view_spec(request: HttpRequest):
    context = context = {
        "title": "Builder",
        "categories": [
            ("Processor", "cpu.svg"),
            ("Cooler", "cooling.svg"),
            ("Motherboard", "mobo.svg"),
            ("Memory", "memory.svg"),
            ("Power Supply", "psu.svg"),
            ("Storage", "storage.svg"),
            ("Case", "case.svg"),
            ("Graphics Card", "gpu.svg"),
            ("Keyboard", "kbm.svg"),
            ("Mouse", "kbm.svg"),
            ("Monitor", "monitor.svg"),
        ],
    }
    return render(request, "shop/spec.html", context)


def save_spec(request: HttpRequest):
    if request.method == "POST":
        # Get component IDs from the form
        cpu_id = request.POST.get("Processor-id")
        cooler_id = request.POST.get("Cooler-id")
        mobo_id = request.POST.get("Motherboard-id")
        memory_id = request.POST.get("Memory-id")
        psu_id = request.POST.get("Power Supply-id")
        storage_id = request.POST.get("Storage-id")
        case_id = request.POST.get("Case-id")
        gpu_id = request.POST.get("Graphics Card-id")
        kb_id = request.POST.get("Keyboard-id")
        mouse_id = request.POST.get("Mouse-id")
        monitor_id = request.POST.get("Monitor-id")

        # Get or create Computer instance
        product_id = f"spec-{''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=10))}"
        new_pc = Computer(
            product_id=product_id,
            name=product_id,
            price=0,
            manufacturer="TLGShop",
            stock=True,
            mf_page="hello/rfg",
            image="media/default.PNG",
        )
        new_pc.save()

        # Create ComputerInternal instances for each component
        component_ids = [
            cpu_id,
            cooler_id,
            mobo_id,
            memory_id,
            psu_id,
            storage_id,
            case_id,
            gpu_id,
            kb_id,
            mouse_id,
            monitor_id,
        ]

        components = []
        for component_id in component_ids:
            if not component_id:
                continue
            component = Component.objects.get(product_id=component_id)
            new_pc.price += component.price
            components.append(component)

        new_pc.components.add(*components)
        new_pc.price = int(new_pc.price * 1.03)
        new_pc.mf_page = f"'/computer/' + {new_pc.pk}"
        new_pc.save()

        data = {
            "product_id": new_pc.product_id,
            "name": new_pc.name,
            "price": new_pc.price,
            "components": [
                {
                    "comp_category": comp.category,
                    "comp_id": comp.product_id,
                    "comp_name": comp.name,
                    "comp_price": comp.price,
                }
                for comp in new_pc.components.all()
            ],
        }

        # return JsonResponse(data)
        rndr = render(request, "shop/spec.html", data)
        return rndr
    return JsonResponse({"error": "bad method"}, status=405)


def spec_view(request):
    context = {
        "title": "Builder",
        "categories": [
            ("Processor", "cpu.svg"),
            ("Cooler", "cooling.svg"),
            ("Motherboard", "mobo.svg"),
            ("Memory", "memory.svg"),
            ("Power Supply", "psu.svg"),
            ("Storage", "storage.svg"),
            ("Case", "case.svg"),
            ("Graphics Card", "gpu.svg"),
            ("Keyboard", "kbm.svg"),
            ("Mouse", "kbm.svg"),
            ("Monitor", "monitor.svg"),
        ],
        "worker": is_worker(request),
    }
    return render(request, "shop/spec.html", context)


def search_spec(request: HttpRequest):
    if request.method == "GET":
        product_id = request.GET.get("product_id")
        computer = Computer.objects.get(product_id=product_id)

        data = {
            "product_id": computer.product_id,
            "name": computer.name,
            "price": computer.price,
            "components": [
                {
                    "comp_category": comp.category,
                    "comp_id": comp.product_id,
                    "comp_name": comp.name,
                    "comp_price": comp.price,
                }
                for comp in computer.components.all()
            ],
        }
        # return JsonResponse(data)
        return render(request, "shop/spec.html", data)
    return JsonResponse({"error": "bad method"}, status=405)


# orders functions
def view_orders(request):
    data = Order.objects.all()
    context = {"title": "Orders", "orders": data, "worker": is_worker(request)}
    return render(request, "shop/orders.html", context)


def is_worker(request):
    worker = request.user.is_authenticated and (
        request.user.groups.filter(name="Worker").exists()
        or request.user.groups.filter(name="Admin").exists()
    )
    return worker
