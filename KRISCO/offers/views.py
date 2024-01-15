from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.db import models
import pandas as pd
from .models import Weekly_Offers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.core.mail import EmailMessage
from io import BytesIO
from django.utils import timezone
import logging
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

logger = logging.getLogger(__name__)

class WeeklyOffersView(View):
    template_name = 'offers.html'

    def get(self, request, *args, **kwargs):
        brand = request.GET.get('brand', '')
        category = request.GET.get('category', '')

        items = Weekly_Offers.objects.all()

        if brand:
            items = items.filter(brand=brand)

        if category:
            items = items.filter(category=category)

        unique_brands = Weekly_Offers.objects.values_list('brand', flat=True).distinct()
        unique_categories = Weekly_Offers.objects.values_list('category', flat=True).distinct()

        context = {
            'items': items,
            'unique_brands': unique_brands,
            'unique_categories': unique_categories,
        }
        return render(request, self.template_name, context)

class AddToPreviewView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        columns = ['SKU', 'UPC', 'Description', 'Quantity', 'Price']
        df = pd.DataFrame(data, columns=columns)

        for index, row in df.iterrows():
            sku = row['SKU']
            entered_quantity = int(row['Quantity'])
            Weekly_Offers.objects.filter(sku=sku).update(available_qty=models.F('available_qty') - entered_quantity)

        return JsonResponse({'success': True})

def update_quantity_view(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        quantity = request.POST.get('quantity')

        try:
            weekly_offer = Weekly_Offers.objects.get(sku=sku)
            weekly_offer.available_qty = quantity
            weekly_offer.save()
            return JsonResponse({'success': True})
        except Weekly_Offers.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Offer not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@method_decorator(csrf_exempt, name='dispatch')
class SubmitPreviewView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.info('Received data: %s', data)

            dataframe = pd.DataFrame(data['previewData'])
            logger.info('DataFrame: %s', dataframe)

            grand_total_row = {
                'sku' : '-',
                'upc' : '-',
                'description': 'Grand Total:',
                'entered_quantity': dataframe['entered_quantity'].sum(),
                'offered_price': dataframe['offered_price'].sum(),
            }

            grand_total_df = pd.DataFrame([grand_total_row])
            dataframe = pd.concat([dataframe, grand_total_df], ignore_index=True)

            workbook = Workbook()
            sheet = workbook.active

            for row in dataframe_to_rows(dataframe, index=False, header=True):
                sheet.append(row)

            for column in sheet.columns:
                max_length = 0
                column = [cell for cell in column]
                max_length = max(len(str(cell.value)) for cell in column)
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[column[0].column_letter].width = adjusted_width

            excel_buffer = BytesIO()
            workbook.save(excel_buffer)
            excel_buffer.seek(0)

            subject = f'ORDER ID - {timezone.now().strftime("%Y-%m-%d-%H:%M:%S.%f")}'
            message = 'Please find the attached Excel file containing the order details.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]
            cc_email = 'support10@pbkriscosales.net'
            recipient_list_with_cc = [request.user.email, cc_email]

            email = EmailMessage(subject, message, from_email, recipient_list_with_cc)
            email.attach('preview_data.xlsx', excel_buffer.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            email.send()

            excel_buffer.close()

            return JsonResponse({'success': True, 'dataframe': dataframe.to_dict(orient='records')})
        except Exception as e:
            logger.error('Error processing preview data: %s', str(e))
            return JsonResponse({'success': False, 'error': 'Failed to process preview data'})

class ThankYouView(View):
    template_name = 'thankyou.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
