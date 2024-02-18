from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.contrib import messages
from django.db import transaction
from .models import Customer
import csv
import logging

logger = logging.getLogger(__name__)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'first_name', 'last_name','mobile_extension','mobile_number', 'email', 'customer_cc_email','customer_bcc_email','customer_type', 'customer_company', 'display_category', 'customer_rank', 'billing_address', 'shipping_address', 'staff_id', 'customer_handler_first_name', 'customer_handler_last_name', 'customer_handler_email')
    search_fields = ['customer_id', 'first_name', 'last_name', 'email']
    list_filter = ('customer_type', 'customer_rank', 'customer_company')
    actions = ['download_csv_template']

    def display_category(self, obj):
        return ", ".join(obj.customer_category)
    display_category.short_description = 'Category'

    def download_csv_template(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customer_template.csv"'
        writer = csv.writer(response)
        # Adjust the headers based on fields users need to fill
        headers = ['first_name', 'last_name', 'mobile_extension', 'mobile_number', 'email', 
                   'customer_cc_email', 'customer_bcc_email', 'customer_type', 'customer_company', 
                   'customer_category', 'customer_rank', 'billing_address', 'shipping_address', 'staff_id']
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
                messages.error(request, 'The wrong file type was uploaded. Please upload a CSV file.')
                return HttpResponseRedirect(request.path_info)

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                with transaction.atomic():
                    for row in reader:
                        # Assuming 'staff_id' is unique and provided in your CSV
                        Customer.objects.update_or_create(
                            staff_id=row.get('staff_id'),
                            defaults={key: value for key, value in row.items()}
                        )
                messages.success(request, 'CSV file has been imported successfully!')
            except Exception as e:
                logger.error(f"Error importing CSV: {e}")
                messages.error(request, 'Something went wrong. Please try again.')
                return HttpResponseRedirect(request.path_info)

            # Dynamically construct the URL for redirection
            app_label = Customer._meta.app_label
            model_name = Customer._meta.model_name
            return HttpResponseRedirect(reverse(f'admin:{app_label}_{model_name}_changelist'))

        # Your form rendering code for GET requests
        template_name = 'admin/import_csv.html'
        return render(request, template_name)
