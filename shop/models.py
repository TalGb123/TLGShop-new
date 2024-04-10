from django.contrib.auth.models import User
from django.db import models

from .utils import image_exists

# Create your models here.


class HumanResources(models.Model):
    id = models.AutoField(primary_key=True)
    person_id = models.CharField(unique=True, max_length=9)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(default="0001-01-01")
    city = models.CharField(max_length=50, null=True)
    street = models.CharField(null=True, max_length=50)
    building_number = models.IntegerField(null=True)
    apartment_number = models.IntegerField(null=True)
    cellphone_number = models.CharField(max_length=10, null=True)
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True)


class Customer(HumanResources):
    membership = models.BooleanField(default=False, null=True)
    ms_points = models.IntegerField(null=True)


class Worker(HumanResources):
    BEERSHEVA = "Beer Sheva"
    EILAT = "Eilat"
    branches: list[tuple[str, str]] = [(BEERSHEVA, "Beer Sheva"), (EILAT, "Eilat")]
    work_branch = models.CharField(max_length=50, choices=branches, default=BEERSHEVA)
    job_title = models.CharField(max_length=50)
    workstart_date = models.DateField(auto_now_add=True)


class Product(models.Model):
    ASUS = "Asus"
    COOLERMASTER = "Coolermaster"
    GIGABYTE = "Gigabyte"
    LIANLI = "Lian Li"
    ANTEC = "Antec"
    CORSAIR = "Corsair"
    SAPPHIRE = "Sapphire"
    AMD = "AMD"
    INTEL = "Intel"

    mf_list: list[tuple[str, str]] = [
        (ASUS, "Asus"),
        (COOLERMASTER, "Coolermaster"),
        (GIGABYTE, "Gigabyte"),
        (LIANLI, "Lian Li"),
        (ANTEC, "Antec"),
        (CORSAIR, "Corsair"),
        (SAPPHIRE, "Sapphire"),
        (AMD, "AMD"),
        (INTEL, "Intel"),
    ]

    id = models.AutoField(primary_key=True)
    product_id = models.CharField(unique=True, max_length=30)
    name = models.CharField(unique=True, max_length=50)
    price = models.IntegerField()
    manufacturer = models.CharField(max_length=50, choices=mf_list, default=ASUS)
    stock = models.BooleanField(default=False, null=True)
    mf_page = models.URLField()
    image = models.ImageField(
        upload_to="product-images",
        default="default.png",
    )

    def __str__(self):
        return f"{self.name}"

    def eilat_price(self):
        return int(float(self.price) * 0.83)

    def save_product_with_image(self, image_path):
        if not image_exists(image_path):
            self.image = image_path
            self.save()
            return True
        else:
            return False


class Component(Product):
    CPU = "Processor"
    GPU = "Graphics Card"
    MOBO = "Motherboard"
    MEMORY = "Memory"
    COOLER = "Cooler"
    STORAGE = "Storage"
    PSU = "Power Supply"
    CASE = "Case"
    KEYBOARD = "Keyboard"
    MOUSE = "Mouse"
    MONITOR = "Monitor"

    category_list: list[tuple[str, str]] = [
        (CPU, "Processor"),
        (GPU, "Graphics Card"),
        (MOBO, "Motherboard"),
        (MEMORY, "Memory"),
        (COOLER, "Cooler"),
        (STORAGE, "Storage"),
        (PSU, "Power Supply"),
        (CASE, "Case"),
        (KEYBOARD, "Keyboard"),
        (MOUSE, "Mouse"),
        (MONITOR, "Monitor"),
    ]

    category = models.CharField(max_length=50, choices=category_list, default=CPU)


class Computer(Product):
    components = models.ManyToManyField(Component, through="ComputerInternal")


class ComputerInternal(models.Model):
    id = models.AutoField(primary_key=True)
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    class Meta:
        unique_together = "computer", "component"


class Order(models.Model):
    CC = "Credit Card"
    CASH = "Cash"

    payment = [(CC, "Credit Card"), (CASH, "Cash")]

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=payment, default=CC)
    products = models.ManyToManyField(Product)
    date = models.DateTimeField(auto_now_add=True)
