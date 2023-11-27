from typing import Any
from django.db.models import Count
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .models import Category, Comment, Customer, Product, Order


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3<=10'
    MORE_THAN_10 = '>10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (self.LESS_THAN_3, 'High'),
            (self.BETWEEN_3_AND_10, 'Medium'),
            (self.MORE_THAN_10, 'Ok'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == self.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == self.BETWEEN_3_AND_10:
            return queryset.filter(inventory__range=(3, 10))
        if self.value() == self.MORE_THAN_10:
            return queryset.filter(inventory__gt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory', 'price', 'inventory_status', 'product_category', 'num_of_comments']
    list_per_page = 20
    list_editable = ['price']
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter]
    actions = ['clear_inventory']
    prepopulated_fields = {
        'slug': ['name']
    }

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('comments').annotate(comments_count=Count('comments'))
    
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        if product.inventory > 50:
            return 'Heigh'
        return 'Medium'
    
    @admin.display(description='# comments', ordering='comments_count')
    def num_of_comments(self, product):
        url = (
            reverse('admin:store_comment_changelist') 
            + '?' 
            + urlencode({
                'product__id': product.id
            })
        )
        return format_html('<a href="{}">{}</a>', url, product.comments_count)
    
    @admin.display(ordering='category__title')
    def product_category(self, product):
        return product.category.title
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} of products inventories cleared to zero.',
        )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'num_of_items']
    list_editable = ['status']
    list_per_page = 10
    ordering = ['-datetime_created']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items').annotate(items_count=Count('items'))

    @admin.display(ordering='items_count', description='# items')
    def num_of_items(self, order):
        return order.items_count


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status']
    list_editable = ['status']
    list_per_page = 10


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


admin.site.register(Category)
