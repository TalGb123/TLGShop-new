import random
from datetime import date

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.detail import DetailView
import http.client
import orjson
from .models import *
from users.views import is_worker
from urllib.parse import urlencode


# Create your views here.


# home functions
def view_home(request: HttpRequest):
    context = {
        "title": "Home",
        "worker": is_worker(request),
        "admin_messages": request_messages(),
    }
    return render(request, "shop/home.html", context)


def view_home_table(request: HttpRequest):
    context = {"admin_messages": request_messages(), "title": "Home"}
    return render(request, "shop/home_table.html", context)


def request_messages():
    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request("GET", "/")
    res = conn.getresponse()
    return orjson.loads(res.read().decode())


def create_message(request: HttpRequest):
    if request.method == "POST":
        subject = request.POST.get("subject")
        content = request.POST.get("content")

        if not (subject and content):
            return HttpResponse("Missing required fields")

        payload = orjson.dumps(
            {
                "subject": subject,
                "content": content,
                "username": request.user.username,
            }
        )
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request(
            "POST",
            f"/insert",
            payload,
        )
        return HttpResponseRedirect("/")


def search_message(request: HttpRequest):
    if request.method == "GET":
        id = request.GET.get("id")
        payload = orjson.dumps(
            {
                "id": id,
            }
        )
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request(
            "POST",
            f"/search",
            payload,
        )
        res = conn.getresponse()
        return JsonResponse(orjson.loads(res.read().decode()))


def update_message(request: HttpRequest):
    if request.method == "POST":
        id = request.POST.get("id")
        subject = request.POST.get("subject")
        content = request.POST.get("content")

        if not (subject and content):
            return HttpResponse("Missing required fields")

        payload = orjson.dumps(
            {
                "id": id,
                "subject": subject,
                "content": content,
            }
        )
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request(
            "POST",
            f"/update",
            payload,
        )
        return HttpResponseRedirect("/")
    return HttpResponse(request)


def delete_message(request: HttpRequest):
    if request.method == "POST":
        id = request.POST.get("id")
        payload = orjson.dumps(
            {
                "id": id,
            }
        )
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request(
            "POST",
            f"/delete",
            payload,
        )


# product functions
def view_products(request: HttpRequest):
    # Retrieve all component objects from the database and convert them into a list
    components = list(Component.objects.all())
    # Currently, the website only displays components. Uncomment the line below to include computers in the product list
    # computers = list(Computer.objects.all())
    # Combine the component and computer lists into a single list
    data = components  # + computers
    # Create a dictionary containing the list of products, the title of the page, the list of known manufacturers, the list of known categories, and a flag indicating whether the user is a worker or not
    context = {
        "products": data,  # List of all products to display on the page
        "title": "Products",  # Title of the page
        "mf_list": Product.mf_list,  # List of known manufacturers for filtering purposes
        "category_list": Component.category_list,  # List of known categories for filtering purposes
        "worker": is_worker(
            request
        ),  # Flag indicating whether the user is a worker or not
    }
    # Render the "shop/products.html" template using the context dictionary and return the result as an HttpResponse object
    return render(request, "shop/products.html", context)


def filter_products(request: HttpRequest):
    """
    This function filters the list of products based on the selected manufacturers and categories.

    Args:
        request (HttpRequest): The HTTP request object containing the GET parameters.

    Returns:
        HttpResponse: The HTTP response object containing the filtered list of products.
    """

    # Retrieve the list of selected manufacturers and categories from the request GET parameters
    selected_manufacturers = request.GET.getlist("manufacturer")
    selected_categories = request.GET.getlist("category")

    # Retrieve all the components from the database
    data = Component.objects.all()

    # If manufacturers are selected, filter the data to only include components with those manufacturers
    if selected_manufacturers:
        data = Component.objects.filter(manufacturer__in=selected_manufacturers)

    # If categories are selected, filter the data to only include components with those categories
    if selected_categories:
        data = data.filter(category__in=selected_categories)

    # Create a dictionary containing the filtered list of products, the title of the page, and a flag indicating whether the user is a worker or not
    context = {
        "products": list(data),  # List of filtered products to display on the page
        "title": "Products",  # Title of the page
        "worker": is_worker(
            request
        ),  # Flag indicating whether the user is a worker or not
    }

    # Render the "shop/product_list.html" template using the context dictionary and return the result as an HttpResponse object
    return render(request, "shop/product_list.html", context)


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
    """
    Update an existing customer's information.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the '/customers/' URL.
    """
    # Get the customer's unique identifier, first name, last name, birth date, city, street, building number,
    # apartment number, cellphone number, account ID, membership status, and Microsoft points from the request.
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

    # Get the customer object from the database using the unique identifier.
    customer = Customer.objects.get(person_id=person_id)

    # Update the customer's information if the corresponding value is not None.
    if first_name is not None:
        customer.first_name = first_name
    if last_name is not None:
        customer.last_name = last_name
    if birth_date is not None:
        customer.birth_date = date.fromisoformat(
            birth_date
        )  # Convert the birth date string to a date object.
    if city is not None:
        customer.city = city
    if street is not None:
        customer.street = street
    if building_number is not None:
        customer.building_number = int(
            building_number
        )  # Convert the building number string to an integer.
    if apartment_number is not None:
        customer.apartment_number = int(
            apartment_number
        )  # Convert the apartment number string to an integer.
    if cellphone_number is not None:
        customer.cellphone_number = cellphone_number
    if account is not None:
        customer.account = User.objects.get(
            pk=int(account)
        )  # Get the User object with the specified ID.
    customer.membership = (
        membership is not None
    )  # Set the membership status to True if membership is not None.
    if ms_points == "":
        customer.ms_points = (
            0  # Set the Microsoft points to 0 if ms_points is an empty string.
        )
    if ms_points is not None:
        customer.ms_points = (
            ms_points  # Set the Microsoft points to the value of ms_points.
        )

    # Save the changes to the customer object in the database.
    customer.save()

    # Redirect to the '/customers/' URL.
    return HttpResponseRedirect("/customers/")


# worker functions


def view_workers(request: HttpRequest):
    data = Worker.objects.all()
    context = {
        "workers": data,
        "title": "Workers",
        "branches": Worker.branches,
        "worker": is_worker(request),
    }
    return render(request, "shop/workers.html", context)


def view_workers_table(request: HttpRequest):
    data = Worker.objects.all()
    context = {"workers": data, "title": "Workers"}
    return render(request, "shop/workers_table.html", context)


def create_worker(request: HttpRequest):
    if request.method != "POST":
        return HttpResponse(request)

    person_id = request.POST.get("person_id")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    birth_date = request.POST.get("birth_date")
    city = request.POST.get("city", "")
    street = request.POST.get("street", "")
    building_number = request.POST.get("building_number", "")
    apartment_number = request.POST.get("apartment_number", "")
    cellphone_number = request.POST.get("cellphone_number", "")
    account = request.POST.get("account")
    work_branch = request.POST.get("work_branch")
    job_title = request.POST.get("job_title")
    workstart_date = request.POST.get("workstart_date")

    if not person_id or not first_name or not last_name or not account:
        print("I've fucked up!!!!!")
        return HttpResponse(request)

    try:
        account_obj = User.objects.get(username=account)
    except User.DoesNotExist:
        return HttpResponse("Account not found")

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
        account=account_obj,
        work_branch=work_branch,
        job_title=job_title,
        workstart_date=workstart_date,
    )
    new_worker.save()

    return HttpResponseRedirect("/workers/")


# This function handles the search of a worker by their person_id
# It is called by the search worker form in the workers page of the shop app
# It expects a GET request with a person_id parameter
# If the worker is found, it returns a JSON response with the worker's data
# If the worker is not found, it returns a JSON response with empty string values
# If the request is not a GET request, it returns a JSON response with an error message
def search_worker(request: HttpRequest):
    # Check if the request method is GET
    if request.method == "GET":
        # Get the person_id parameter from the request
        person_id = request.GET.get("person_id")
        try:
            # Try to get the worker object with the matching person_id
            worker = Worker.objects.get(person_id=person_id)
            # Create a dictionary with the worker's data
            data = {
                "person_id": worker.person_id,  # person_id of the worker
                "first_name": worker.first_name,  # first name of the worker
                "last_name": worker.last_name,  # last name of the worker
                "birth_date": worker.birth_date,  # birth date of the worker
                "city": worker.city,  # city of the worker
                "street": worker.street,  # street of the worker
                "building_number": worker.building_number,  # building number of the worker
                "apartment_number": worker.apartment_number,  # apartment number of the worker
                "cellphone_number": worker.cellphone_number,  # cellphone number of the worker
                "account": worker.account.pk,  # account ID of the worker
                "work_branch": worker.work_branch,  # work branch of the worker
                "job_title": worker.job_title,  # job title of the worker
                "workstart_date": worker.workstart_date,  # work start date of the worker
            }
            # Return a JSON response with the worker's data
            return JsonResponse(data)
        except Worker.DoesNotExist:
            # If the worker is not found, create an empty dictionary with empty string values
            empty_worker = {
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
            }
            # Return a JSON response with the empty dictionary and a 404 status code
            return JsonResponse(empty_worker, status=404)
    else:
        # If the request is not a GET request, return a JSON response with an error message and a 405 status code
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
    # Get the worker's data from the request
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

    # Get the worker object with the matching person_id
    worker = Worker.objects.get(person_id=person_id)

    # Update the worker's data if the corresponding data is not None
    if first_name is not None:
        worker.first_name = first_name  # Update the first name of the worker
    if last_name is not None:
        worker.last_name = last_name  # Update the last name of the worker
    if birth_date is not None:
        worker.birth_date = date.fromisoformat(
            birth_date
        )  # Update the birth date of the worker
    if city is not None:
        worker.city = city  # Update the city of the worker
    if street is not None:
        worker.street = street  # Update the street of the worker
    if building_number is not None:
        worker.building_number = int(
            building_number
        )  # Update the building number of the worker
    if apartment_number is not None:
        worker.apartment_number = int(
            apartment_number
        )  # Update the apartment number of the worker
    if cellphone_number is not None:
        worker.cellphone_number = (
            cellphone_number  # Update the cellphone number of the worker
        )
    if account is not None:
        worker.account = User.objects.get(
            pk=int(account)
        )  # Update the account of the worker
    if work_branch is not None:
        worker.work_branch = work_branch  # Update the work branch of the worker
    if job_title is not None:
        worker.job_title = job_title  # Update the job title of the worker
    if workstart_date is not None:
        worker.workstart_date = date.fromisoformat(
            workstart_date
        )  # Update the work start date of the worker

    # Save the updated worker object
    worker.save()

    # Redirect the user to the workers page
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
    """
    This function handles GET requests to filter products by category and returns a JSON response
    with the serialized products. It expects a 'category' parameter in the request query string.
    If the request method is not GET, it returns a JSON response with an 'error' field.
    """
    # Check if the request method is GET
    if request.method == "GET":
        # Get the 'category' parameter from the request query string
        category = request.GET.get("category")
        # Query the database for products that match the given category
        products = Component.objects.filter(category=category)
        # Serialize the products into a list of dictionaries
        serialized_products = [
            # For each product, create a dictionary with its primary key and fields
            {
                "pk": product.pk,  # Primary key of the product
                "fields": {
                    "product_id": product.product_id,  # Product ID
                    "category": product.category,  # Category of the product
                    "name": product.name,  # Name of the product
                    "price": product.price,  # Price of the product
                    "image": product.image.url,  # Convert ImageField to string
                    "mf_page": product.mf_page,  # Manufacturer's page URL
                    # Add other fields as needed
                },
            }
            # Iterate over all products
            for product in products
        ]
        # Return a JSON response with the serialized products
        return JsonResponse({"products": serialized_products})
    # If the request method is not GET, return an error JSON response
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
    """
    Save specification and create a new Computer instance with the specified components.
    Return a JSON response containing the product ID, name, price, and a list of components.
    """
    # Check if the request method is POST
    if request.method == "POST":
        # Get component IDs from the form
        cpu_id = request.POST.get("Processor-id")  # Get CPU ID
        cooler_id = request.POST.get("Cooler-id")  # Get Cooler ID
        mobo_id = request.POST.get("Motherboard-id")  # Get Motherboard ID
        memory_id = request.POST.get("Memory-id")  # Get Memory ID
        psu_id = request.POST.get("Power Supply-id")  # Get Power Supply ID
        storage_id = request.POST.get("Storage-id")  # Get Storage ID
        case_id = request.POST.get("Case-id")  # Get Case ID
        gpu_id = request.POST.get("Graphics Card-id")  # Get Graphics Card ID
        kb_id = request.POST.get("Keyboard-id")  # Get Keyboard ID
        mouse_id = request.POST.get("Mouse-id")  # Get Mouse ID
        monitor_id = request.POST.get("Monitor-id")  # Get Monitor ID

        # Generate a random product ID
        product_id = f"{''.join(random.choices('1234567890', k=6))}"

        # Create a new Computer instance with the specified components
        new_pc = Computer(
            product_id=product_id,  # Set the product ID
            name=product_id,  # Set the name to the product ID
            price=0,  # Set the price to 0
            manufacturer="TLGShop",  # Set the manufacturer to "TLGShop"
            stock=True,  # Set stock to True
            mf_page="hello/rfg",  # Set the manufacturer page to "hello/rfg"
            image="media/default.PNG",  # Set the image to "media/default.PNG"
        )
        new_pc.save()  # Save the new_pc instance

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

        components = []  # Create an empty list to store the components
        for component_id in component_ids:
            if not component_id:  # If the component ID is empty, skip it
                continue
            component = Component.objects.get(
                product_id=component_id
            )  # Get the component instance
            new_pc.price += (
                component.price
            )  # Add the component price to the new_pc price
            components.append(component)  # Add the component to the components list

        new_pc.components.add(*components)  # Add the components to the new_pc instance
        new_pc.price = int(new_pc.price * 1.03)  # Add 3% tax to the price
        new_pc.mf_page = f"'/computer/' + {new_pc.pk}"  # Set the manufacturer page to the product page
        new_pc.save()  # Save the new_pc instance

        # Create a dictionary containing the product ID, name, price, and components
        data = {
            "product_id": new_pc.product_id,  # Set the product ID
            "name": new_pc.name,  # Set the name to the product ID
            "price": new_pc.price,  # Set the price
            "components": [
                {
                    "comp_category": comp.category,  # Set the component category
                    "comp_id": comp.product_id,  # Set the component ID
                    "comp_name": comp.name,  # Set the component name
                    "comp_price": comp.price,  # Set the component price
                }
                for comp in new_pc.components.all()  # Get all the components
            ],
        }

        # Return a JSON response containing the data
        # rndr = render(request, "shop/spec.html", data)
        # return rndr
        return render(request, "shop/spec.html", data)
    return JsonResponse(
        {"error": "bad method"}, status=405
    )  # Return a JSON response with an error message and a 405 status code


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
    """
    This function handles GET requests to the '/search_spec' endpoint.
    It retrieves a computer object based on the product ID provided in the request parameters.
    It then creates a dictionary containing the computer's product ID, name, price, and a list of its components.
    The function returns a JSON response containing the computer's data, or a JSON response with an error message and a 405 status code if the request method is not GET.
    """

    # Check if the request method is GET
    if request.method == "GET":
        # Get the product ID from the request parameters
        product_id = request.GET.get("product_id")

        # Retrieve the computer object based on the product ID
        computer = Computer.objects.get(product_id=product_id)

        # Create a dictionary containing the computer's data
        data = {
            "product_id": computer.product_id,  # Set the product ID
            "name": computer.name,  # Set the computer name
            "price": computer.price,  # Set the price
            "components": [
                {
                    "comp_category": comp.category,  # Set the component category
                    "comp_id": comp.product_id,  # Set the component ID
                    "comp_name": comp.name,  # Set the component name
                    "comp_price": comp.price,  # Set the component price
                }
                for comp in computer.components.all()  # Get all the computer's components
            ],
        }

        # Return a JSON response containing the computer's data
        # return JsonResponse(data)
        return render(
            request, "shop/spec.html", data
        )  # Render the 'spec.html' template with the data
    # Return a JSON response with an error message and a 405 status code if the request method is not GET
    return JsonResponse({"error": "bad method"}, status=405)


def is_worker(request):
    worker = request.user.is_authenticated and (
        request.user.groups.filter(name="Worker").exists()
        or request.user.groups.filter(name="Admin").exists()
    )
    return worker
