from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from .models import Item,Stock,InOutReport
import csv
import io
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('sku', 'description', 'brand', 'upc', 'unit_weight', 'price', 'classification', 'notes')
    search_fields = ['sku', 'description', 'brand','upc']
    list_filter = ('classification',)

    actions = ['download_csv_template']

    def download_csv_template(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="item_template.csv"'
        writer = csv.writer(response)
        headers = ['sku', 'description', 'brand', 'upc', 'unit_weight', 'price', 'classification', 'notes']
        writer.writerow(headers)
        return response

    download_csv_template.short_description = "Download CSV template for items"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-txt/', self.admin_site.admin_view(self.import_txt), name='inventory_item_import_txt'),
        ]
        return custom_urls + urls

    def import_txt(self, request):
        if request.method == 'POST':
            txt_file = request.FILES.get('txt_file')

            if not txt_file:
                messages.error(request, "No file was uploaded.")
                return HttpResponseRedirect(request.path_info)

            if not txt_file.name.endswith('.txt'):
                messages.error(request, "Invalid file format. Please upload a TXT file.")
                return HttpResponseRedirect(request.path_info)

            try:
                file_data = txt_file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    txt_file.seek(0)  # Reset file pointer to the beginning
                    file_data = txt_file.read().decode('ISO-8859-1')
                except UnicodeDecodeError as e:
                    logger.error(f"Error processing TXT file: {e}")
                    messages.error(request, "An error occurred while processing the TXT file. Unsupported file encoding.")
                    return HttpResponseRedirect(request.path_info)

            csv_data = csv.reader(io.StringIO(file_data), delimiter='\t')
            header = next(csv_data)
            expected_header = ['sku', 'description', 'brand', 'upc', 'unit_weight', 'price', 'classification', 'notes']

            if header != expected_header:
                messages.error(request, "Invalid TXT header.")
                return HttpResponseRedirect(request.path_info)

            with transaction.atomic():
                for row in csv_data:
                    if len(row) != len(expected_header):
                        continue  # Skip rows with incorrect number of columns
                    obj, created = Item.objects.update_or_create(
                        sku=row[0],
                        defaults={
                            'description': row[1],
                            'brand': row[2],
                            'upc': row[3] if row[3] else 'NO UPC',
                            'unit_weight': float(row[4]) if row[4] else 0.00,
                            'price': float(row[5]) if row[5] else 0.00,
                            'classification': row[6] if row[6] in dict(Item.CLASSIFICATION_CHOICES) else '',
                            'notes': row[7] if len(row) > 7 else ''
                        }
                    )
                    if created:
                        logger.info(f"Created new Item: {obj.sku}")
                    else:
                        logger.info(f"Updated Item: {obj.sku}")

            messages.success(request, "TXT file imported successfully.")
            return HttpResponseRedirect('../')

        context = {'title': 'Import TXT for Items'}
        return render(request, 'admin/import_txt.html', context)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('sku', 'upc', 'item_classification', 'description', 'on_hand', 'allocated', 'available', 'cost')
    search_fields = ['sku', 'description', 'item_classification', 'upc']
    list_filter = ('item_classification',)

    actions = ['download_csv_template']

    def download_csv_template(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_template.csv"'
        
        writer = csv.writer(response, delimiter='\t')
        headers = ['SKU', 'UPC', 'Item Classification', 'Description', 'OnHand', 'Allocated', 'Available', 'Cost']
        writer.writerow(headers)
        
        return response

    download_csv_template.short_description = "Download CSV template for stock"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-txt/', self.admin_site.admin_view(self.import_txt), name='inventory_stock_import_txt'),
        ]
        return custom_urls + urls

    def import_txt(self, request):
        if request.method == 'POST':
            txt_file = request.FILES.get('txt_file')

            if not txt_file:
                messages.error(request, "No file was uploaded.")
                return HttpResponseRedirect(request.path_info)

            if not txt_file.name.endswith('.txt'):
                messages.error(request, "Invalid file format. Please upload a TXT file.")
                return HttpResponseRedirect(request.path_info)

            try:
                file_data = txt_file.read().decode('utf-8')
                lines = file_data.splitlines()
                csv_data = csv.reader(lines, delimiter='\t')
                header = next(csv_data)
                expected_header = ['SKU', 'UPC', 'Item Classification', 'Description', 'OnHand', 'Allocated', 'Available', 'Cost']
                
                if header != expected_header:
                    messages.error(request, "Invalid TXT header.")
                    return HttpResponseRedirect(request.path_info)

                with transaction.atomic():
                    for row in csv_data:
                        if len(row) != len(expected_header):
                            continue  # Skip rows with missing or extra columns

                        # Convert empty strings to None (null)
                        row = [None if not cell else cell for cell in row]

                        obj, created = Stock.objects.update_or_create(
                            sku=row[0],
                            defaults={
                                'upc': row[1] if row[1] else 'NO UPC',
                                'item_classification': row[2] if row[6] in dict(Item.CLASSIFICATION_CHOICES) else '',
                                'description': row[3],
                                'on_hand': int(row[4]) if row[4] else 0,
                                'allocated': int(row[5]) if row[5] else 0,
                                'available': int(row[6]) if row[6] else 0,
                                'cost': float(row[7]) if row[7] else 0.00
                            }
                        )
                        if created:
                            logger.info(f"Created new Stock: {obj.sku}")
                        else:
                            logger.info(f"Updated Stock: {obj.sku}")

                messages.success(request, "TXT file imported successfully.")
                return HttpResponseRedirect('../')

            except Exception as e:
                logger.error(f"Error processing TXT file: {e}")
                messages.error(request, "An error occurred while processing the TXT file.")
                return HttpResponseRedirect(request.path_info)

        context = {'title': 'Import TXT for Stock'}
        return render(request, 'admin/import_txt.html', context)
    

@admin.register(InOutReport)
class InOutReportAdmin(admin.ModelAdmin):
    list_display = ('sku', 'item_description', 'qty_in', 'qty_out', 'balance')
    search_fields = ['sku', 'item_description']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-txt/', self.admin_site.admin_view(self.import_txt), name='inoutreport_import_txt'),
        ]
        return custom_urls + urls

    def import_txt(self, request):
        if request.method == 'POST':
            txt_file = request.FILES.get('txt_file')

            if not txt_file:
                messages.error(request, "No file was uploaded.")
                return HttpResponseRedirect(request.path_info)

            try:
                decoded_file = txt_file.read().decode('utf-8').splitlines()
                reader = csv.reader(io.StringIO('\n'.join(decoded_file)), delimiter='\t')

                # Check headers
                headers = next(reader, None)
                expected_headers = ['SKU', 'Item Description', 'Qty in', 'Qty out', 'Balance']
                if headers != expected_headers:
                    messages.error(request, f"Invalid headers. Expected headers are: {expected_headers}")
                    return HttpResponseRedirect(request.path_info)

                with transaction.atomic():
                    for row in reader:
                        # Skip empty rows
                        if not ''.join(row).strip():
                            continue

                        # Validate row length
                        if len(row) != len(expected_headers):
                            messages.error(request, "Row length does not match the expected format.")
                            return HttpResponseRedirect(request.path_info)

                        sku, item_description, qty_in, qty_out, balance = row

                        # Convert numerical values safely
                        try:
                            qty_in = int(qty_in) if qty_in else 0
                            qty_out = int(qty_out) if qty_out else 0
                            balance = int(balance) if balance else 0
                        except ValueError:
                            messages.error(request, "Invalid data format in the row.")
                            return HttpResponseRedirect(request.path_info)

                        InOutReport.objects.update_or_create(
                            sku=sku,
                            defaults={
                                'item_description': item_description,
                                'qty_in': qty_in,
                                'qty_out': qty_out,
                                'balance': balance
                            }
                        )

                messages.success(request, "TXT file imported successfully.")
                return HttpResponseRedirect('../')

            except Exception as e:
                logger.error(f"Error processing TXT file: {e}")
                messages.error(request, "An error occurred while processing the TXT file.")
                return HttpResponseRedirect(request.path_info)

        context = {'title': 'Import TXT for In & Out Report'}
        return render(request, 'admin/import_txt.html', context)


    






