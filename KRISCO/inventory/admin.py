from django.utils import timezone
from django.urls import path, reverse
from django.contrib import admin
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
import pandas as pd
from .models import Item,Stock,InOutReport,SlowMoversReport
import csv
from decimal import Decimal, InvalidOperation
import io
import logging
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from daterange.filters import DateRangeFilter



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

# Setup logger
logger = logging.getLogger(__name__)

def safe_decimal_conversion(value, default=Decimal(0)):
    try:
        return Decimal(str(value))
    except InvalidOperation:
        logger.error(f"Decimal conversion error for value: {value}")
        return default

@admin.register(SlowMoversReport)
class SlowMoversReportAdmin(admin.ModelAdmin):
    list_display = ['sku', 'upc', 'brand','item_classification', 'description', 'qtyin_oneyear', 'qtyout_oneyear', 'balance_oneyear', 'available', 'cost', 'sellercategory']
    list_filter = (('report_date', DateRangeFilter),'sellercategory','item_classification','brand')
    search_fields = ['sku', 'upc', 'item_classification', 'description', 'qtyin_oneyear', 'qtyout_oneyear', 'balance_oneyear', 'available', 'cost', 'sellercategory']
    actions = ['generate_slow_movers_report']

    
    def generate_slow_movers_report(self, request, queryset):
        # Fetch data from Stock and InOutReport models
        stock_data = Stock.objects.all().values()
        in_out_data = InOutReport.objects.all().values()

        # Convert to pandas DataFrame
        df_stock = pd.DataFrame(stock_data)
        df_in_out = pd.DataFrame(in_out_data)

        # Clean and process the DataFrame
        df_stock['available'] = df_stock['available'].fillna(0)
        df_stock['allocated'] = df_stock['allocated'].fillna(0)
        df_stock['item_classification'] = df_stock['item_classification'].fillna('UNKNOWN')

        # Remove specific suffixes from SKU
        suffixes_to_remove = ['-D', '-NZ', '-HK', '-SING', '-R', '-X', '-NL','-NC','NOBOX', '-NO BOX', '-TESTER', '-SAMPLE', '-SAMPLES', '-SAMPLER', '-SAMPLE KIT']
        for suffix in suffixes_to_remove:
            df_stock = df_stock[~df_stock['sku'].str.endswith(suffix, na=False)]

        # Prepare the final DataFrame
        df_final = df_stock[['sku', 'upc', 'item_classification', 'description', 'available', 'cost']].copy()
        df_final['qtyin_oneyear'] = df_final['sku'].map(df_in_out.groupby('sku')['qty_in'].sum())
        df_final['qtyout_oneyear'] = df_final['sku'].map(df_in_out.groupby('sku')['qty_out'].sum())
        df_final['balance_oneyear'] = df_final['sku'].map(df_in_out.groupby('sku')['balance'].sum())

        # Calculate additional fields
        df_final['begining_balance'] = df_final['balance_oneyear'] - df_final['qtyin_oneyear'] + df_final['qtyout_oneyear']
        df_final['reference'] = df_final['qtyin_oneyear'] + df_final['balance_oneyear']
        df_final['percentage'] = df_final.apply(lambda x: safe_decimal_conversion((x['qtyout_oneyear'] / x['reference']) * 100 if x['reference'] else 0), axis=1)

        # Assign SellerCategory based on conditions
        df_final['sellercategory'] = 'Dead Seller'  # Default value
        df_final.loc[(df_final['percentage'] > 20) & (df_final['percentage'] < 80), 'sellercategory'] = 'Average Seller'
        df_final.loc[df_final['percentage'] > 80, 'sellercategory'] = 'Best Seller'
        df_final.loc[df_final['percentage'] < 20, 'sellercategory'] = 'Slow Seller'

        # Save to SlowMoversReport model
        for _, row in df_final.iterrows():
            try:
                item = Item.objects.get(sku=row['sku'])
                brand = item.brand if item else None
                if not brand:
                    # If Item not found, extract brand from the description
                    description_parts = row['description'].split('-')
                    if len(description_parts) >= 2:
                        brand = description_parts[0].strip()
                    else:
                        brand = 'UNKNOWN'
                SlowMoversReport.objects.update_or_create(
                    report_date=timezone.now(),
                    sku=row['sku'],
                    defaults={
                        'upc': row['upc'],
                        'item_classification': row['item_classification'],
                        'description': row['description'],
                        'qtyin_oneyear': int(row['qtyin_oneyear']) if row['qtyin_oneyear'] else 0,
                        'qtyout_oneyear': int(row['qtyout_oneyear']) if row['qtyout_oneyear'] else 0,
                        'balance_oneyear': int(row['balance_oneyear']) if row['balance_oneyear'] else 0,
                        'available': int(row['available']) if row['available'] else 0,
                        'cost': safe_decimal_conversion(row['cost']),
                        'begining_balance': int(row['begining_balance']) if row['begining_balance'] else 0,
                        'reference': int(row['reference']) if row['reference'] else 0,
                        'percentage': safe_decimal_conversion(row['percentage'], 2),
                        'sellercategory': row['sellercategory'],
                        'brand': brand, 
                    }
                )
            except Exception as e:
                logger.error(f"Error saving record for SKU {row['sku']}: {e}")
                continue

        messages.success(request, "Slow Movers Report generated successfully.")

    class Media:
            css = {"all": ("admin/css/forms.css", "css/admin/daterange.css")}
            js = ("admin/js/calendar.js", "js/admin/DateRangeShortcuts.js")



   





