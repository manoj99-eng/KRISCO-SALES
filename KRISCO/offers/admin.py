# admin.py
from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from .models import Weekly_Offers
import csv
import logging

logger = logging.getLogger(__name__)

@admin.register(Weekly_Offers)
class Weekly_OffersAdmin(admin.ModelAdmin):
    actions = ['download_csv_template']

    def download_csv_template(self, request, queryset):
        # Create a CSV template
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="weekly_offers_template.csv"'

        writer = csv.writer(response)
        writer.writerow(['sku', 'upc', 'description', 'brand', 'category', 'available_qty', 'msrp', 'discount', 'offer_price', 'required_quantity'])

        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='import-csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == 'POST' and 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8')
            csv_reader = csv.reader(decoded_file.splitlines(), delimiter=',')

            # Skip the header row
            next(csv_reader)

            try:
                with transaction.atomic():
                    for row in csv_reader:
                        # Handle each field type conversion
                        try:
                            sku = str(row[0])  # Assuming sku is a CharField
                            upc = int(row[1])  # Assuming upc is a BigIntegerField
                            description = str(row[2])  # Assuming description is a CharField
                            brand = str(row[3])  # Assuming brand is a CharField
                            category = str(row[4])  # Assuming category is a CharField

                            # Handle the 'available_qty' field
                            available_qty = int(row[5])

                            msrp = float(row[6])  # Assuming msrp is a FloatField
                            discount = float(row[7])  # Assuming discount is a FloatField
                            offer_price = float(row[8])  # Assuming offer_price is a FloatField

                            # Handle the 'required_quantity' field
                            required_qunatity = int(row[9])

                        except (ValueError, TypeError):
                            # Handle errors based on your requirements
                            # You might want to log the error or set default values
                            logger.error(f"Error importing CSV row: {row}")
                            continue  # Skip this row and move to the next one

                        Weekly_Offers.objects.create(
                            sku=sku,
                            upc=upc,
                            description=description,
                            brand=brand,
                            category=category,
                            available_qty=available_qty,
                            msrp=msrp,
                            discount=discount,
                            offer_price=offer_price,
                            required_qunatity=required_qunatity  # Correct field name
                        )

                    self.message_user(request, "CSV file imported successfully.")
                    return HttpResponseRedirect('../')

            except Exception as e:
                logger.error(f"Error importing CSV: {e}")

        context = dict(
            self.admin_site.each_context(request),
            title='Import CSV',
            action='import-csv',
        )
        return render(request, 'admin/import_csv.html', context)
