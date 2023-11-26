from django.db.models import Count
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import Category, Comment, Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory', 'price', 'inventory_status', 'product_category']
    list_per_page = 20
    list_editable = ['price']
    list_select_related = ['category']
    
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        if product.inventory > 50:
            return 'Heigh'
        return 'Medium'
    
    @admin.display(ordering='category__title')
    def product_category(self, product):
        return product.category.title


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'num_of_items']
    list_editable = ['status']
    list_per_page = 10
    ordering = ['-datetime_created']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items').annotate(items_count=Count('items'))

    @admin.display(ordering='items_count')
    def num_of_items(self, order):
        return order.items_count


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status']
    list_editable = ['status']
    list_per_page = 10


admin.site.register(Category)
