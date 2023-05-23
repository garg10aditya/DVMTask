from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from store.models import Order

# Define the admin class for the Order model
class OrderAdmin(ImportExportModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'total_cost', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('id', 'first_name', 'last_name', 'created_by__username', 'created_by__email')
    ordering = ('-id',)
    date_hierarchy = 'created_at'


admin.site.register(Order, OrderAdmin)
