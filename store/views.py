from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import F, ExpressionWrapper, DecimalField

from .models import Product, Customer, OrderItem, Comment, Order


def show_data(request):
    queryset = Order.objects.get_order_by_status(status=Order.ORDER_STATUS_CANCELED)
    print(queryset)
    return render(request, 'hello.html', context={'products': queryset})

