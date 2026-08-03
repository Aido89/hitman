from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.constructor, name="constructor"),
    path("submit/", views.submit_lead, name="submit_lead"),
    path("my/", views.my_orders, name="my_orders"),
]
