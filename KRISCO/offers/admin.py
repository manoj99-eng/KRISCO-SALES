from django.urls import path,reverse
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from .models import Weekly_Offer
import csv
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

@admin.register(Weekly_Offer)
class Weekly_OfferAdmin(admin.ModelAdmin):
    list_display = ('sku', 'upc', 'description', 'brand', 'display_category', 'available_qty', 'msrp', 'discount', 'offer_price', 'required_quantity')
    search_fields = ['sku', 'description', 'brand', 'category']
    actions = ['download_csv_template']

    def display_category(self, obj):
        return obj.get_category_display()
    display_category.short_description = 'Category'
    

    def download_csv_template(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Weekly_Offer_template.csv"'
        writer = csv.writer(response)
        headers = [field.name for field in Weekly_Offer._meta.get_fields() if field.name != 'id']
        writer.writerow(headers)
        return response

    download_csv_template.short_description = "Download CSV template for weekly offers"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='import-csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
            if request.method == 'POST':
                csv_file = request.FILES.get('csv_file')

                # Check if a file was uploaded
                if not csv_file:
                    messages.error(request, "No file was uploaded.")
                    return HttpResponseRedirect(request.path_info)

                # Check if the uploaded file is a CSV file
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, "Invalid file format. Please upload a CSV file.")
                    return HttpResponseRedirect(request.path_info)

                try:
                    # Read and decode the file, then create a CSV reader object
                    file_data = csv_file.read().decode('utf-8')
                    csv_data = csv.reader(file_data.splitlines())

                    # Check if the header of the CSV matches the expected format
                    header = next(csv_data)
                    expected_header = ['sku', 'upc', 'description', 'brand', 'category', 'available_qty', 'msrp', 'discount', 'offer_price', 'required_quantity']
                    if header != expected_header:
                        messages.error(request, "Invalid CSV header.")
                        return HttpResponseRedirect(request.path_info)

                    # Process each row in the CSV
                    with transaction.atomic():
                        for row in csv_data:
                            obj, created = Weekly_Offer.objects.update_or_create(
                                sku=row[0],
                                defaults={
                                    'upc': int(row[1]),
                                    'description': row[2],
                                    'brand': row[3],
                                    'category': row[4],
                                    'available_qty': int(row[5]),
                                    'msrp': float(row[6]),
                                    'discount': float(row[7]),
                                    'offer_price': float(row[8]),
                                    'required_quantity': int(row[9])
                                }
                            )
                            if created:
                                logger.info(f"Created new Weekly_Offer: {obj.sku}")
                            else:
                                logger.info(f"Updated Weekly_Offer: {obj.sku}")

                    messages.success(request, "CSV file imported successfully.")
                    return HttpResponseRedirect('../')

                except Exception as e:
                    # Log any errors that occur during file processing
                    logger.error(f"Error processing CSV file: {e}")
                    messages.error(request, "An error occurred while processing the CSV file.")
                    return HttpResponseRedirect(request.path_info)

            # Render the CSV import form
            context = {
                'title': 'Import CSV for Weekly Offers',
            }
            return render(request, 'admin/import_csv.html', context)

