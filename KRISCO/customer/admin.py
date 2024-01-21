from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.db import transaction
from .models import Customer
import csv
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'first_name', 'last_name', 'email', 'customer_type', 'customer_company', 'display_category', 'customer_rank', 'billing_address', 'shipping_address', 'handler_first_name', 'handler_last_name', 'handler_email')
    search_fields = ['customer_id', 'first_name', 'last_name', 'email']
    list_filter = ('customer_type', 'customer_rank', 'customer_company')  # Add fields to filter by
    actions = ['download_csv_template']

    def display_category(self, obj):
        return ", ".join(obj.customer_category)
    display_category.short_description = 'Category'

    def download_csv_template(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Customer_template.csv"'
        writer = csv.writer(response)
        headers = [field.name for field in Customer._meta.get_fields() if field.name != 'id']
        writer.writerow(headers)
        return response

    download_csv_template.short_description = "Download CSV template for customers"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='import-csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')

            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, "Invalid file format. Please upload a CSV file.")
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode('utf-8')
            csv_data = csv.reader(file_data.splitlines())
            header = next(csv_data)
            expected_header = [field.name for field in Customer._meta.get_fields() if field.name != 'id']

            if header != expected_header:
                messages.error(request, "Invalid CSV header.")
                return HttpResponseRedirect(request.path_info)

            try:
                with transaction.atomic():
                    for row in csv_data:
                        Customer.objects.update_or_create(
                            customer_id=row[0],
                            defaults={
                                'first_name': row[1],
                                'last_name': row[2],
                                'mobile_extension': int(row[3]),
                                'mobile_number': row[4],
                                'email': row[5],
                                'customer_type': row[6],
                                'customer_company': row[7],
                                'customer_category': row[8].split(','),
                                'customer_rank': row[9],
                                'billing_address': row[10],
                                'shipping_address': row[11],
                                'handler_first_name': row[12],
                                'handler_last_name': row[13],
                                'handler_email': row[14]
                            }
                        )
                messages.success(request, "CSV file imported successfully.")
            except Exception as e:
                logger.error(f"Error importing CSV: {e}")
                messages.error(request, "An error occurred while importing the CSV file.")
            
            return HttpResponseRedirect('../')

        context = {
            'title': 'Import CSV for Customers',
        }
        return render(request, 'admin/import_csv.html', context)

