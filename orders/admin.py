from django.contrib import admin
from .models import Product, Option, AddOn, Cart, Cart_AddOn, Order, Order_Item
from django.utils.translation import ugettext_lazy as _

# Register your models here.

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class AddOnInline(admin.TabularInline):
    model = AddOn
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [OptionInline, AddOnInline]
    list_display = ('name', 'price', 'published')

class OrderInline(admin.TabularInline):
    model = Order_Item

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class StatusFilter(admin.SimpleListFilter):
    title = _('status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            (None, _('paid')),
            ('pending', _('pending')),
            ('completed', _('completed')),
            ('canceled', _('canceled')),
            ('all', _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() in ('pending', 'completed', 'canceled'):
            return queryset.filter(status=self.value())    
        elif self.value() == None:
            return queryset.filter(status='paid')

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'total')

    fields = ('user', 'total', 'status')

    inlines = [OrderInline]
    list_display = ('id', 'get_name', 'total', 'date', 'status')
    list_filter = [StatusFilter, 'date', 'user']
    actions = ['mark_completed', 'mark_canceled']

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            kwargs['choices'] = (
                ('paid', 'paid'),
                ('completed', 'completed'),
                ('canceled', 'canceled'),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_name(self, obj):
        return obj.user.first_name
    get_name.admin_order_field  = 'user'
    get_name.short_description = 'Customer Name'

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Mark selected orders as completed"

    def mark_canceled(self, request, queryset):
        queryset.update(status='canceled')
    mark_canceled.short_description = "Mark selected orders as canceled"

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)

admin.site.site_header = 'Food Delivery Administration'
admin.site.site_title = 'Food Delivery admin'