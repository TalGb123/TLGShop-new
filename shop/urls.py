from django.urls import path

from . import views
from .views import ProductDetailView

# URL Config

urlpatterns = [
    # home urls
    path("", views.view_home, name="view-home"),
    path("/messages", views.view_home_table, name="view-home-table"),
    # product urls
    path("products/", views.view_products, name="view-products"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/component-create", views.create_component, name="create-component"),
    path("products/search", views.search_product, name="search-product"),
    path("products/delete", views.delete_product, name="delete-product"),
    path("products/update", views.update_product, name="update-product"),
    path("products/filter", views.filter_products, name="filter-products"),
    # customer urls
    path("customers/", views.view_customers, name="view-customers"),
    path("customers/table", views.view_customers_table, name="view-customers-table"),
    path("customers/create", views.create_customer, name="create-customer"),
    path("customers/search", views.search_customer, name="search-customer"),
    path("customers/update", views.update_customer, name="update-customer"),
    path("customers/delete", views.delete_customer, name="delete-customer"),
    # worker urls
    path("workers/", views.view_workers, name="view-workers"),
    path("workers/table", views.view_workers_table, name="view-workers-table"),
    path("workers/create", views.create_worker, name="create-worker"),
    path("workers/search", views.search_worker, name="search-worker"),
    path("workers/update", views.update_worker, name="update-worker"),
    path("workers/delete", views.delete_worker, name="delete-worker"),
    # builder urls
    path("builder/", views.view_builder, name="view-builder"),
    path("builder/table", views.view_builder_table, name="view-builder-table"),
    path("builder/category-view/", views.category_list, name="category-view"),
    path("builder/save", views.save_spec, name="save-spec"),
    path("builder/view-spec", views.view_spec, name="view-spec"),
    path("builder/search", views.search_spec, name="search-spec"),
    # order urls
    path("orders/", views.view_orders, name="view-orders"),
]
