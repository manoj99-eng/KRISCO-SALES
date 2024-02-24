from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.mail import EmailMessage
from django.core import serializers
from io import BytesIO
from django.utils import timezone
import logging
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd

from order.models import Order

logger = logging.getLogger(__name__)

class WeeklyOffersView(View):
    template_name = 'offers.html'

    def get(self, request, *args, **kwargs):
        brand = request.GET.get('brand', '')
        category = request.GET.get('category', '')

        items = Weekly_Offer.objects.all()
        if brand:
            items = items.filter(brand=brand)
        if category:
            items = items.filter(category=category)

        unique_brands = set(items.values_list('brand', flat=True))
        unique_categories = set(items.values_list('category', flat=True))

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
            Weekly_Offer.objects.filter(sku=sku).update(available_qty=models.F('available_qty') - entered_quantity)

        return JsonResponse({'success': True})

def update_quantity_view(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        quantity = request.POST.get('quantity')

        try:
            weekly_offer = Weekly_Offer.objects.get(sku=sku)
            weekly_offer.available_qty = quantity
            weekly_offer.save()
            return JsonResponse({'success': True})
        except Weekly_Offer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Offer not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@method_decorator(csrf_exempt, name='dispatch')
class SubmitPreviewView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Assuming request.body contains the necessary data in JSON format
            data = json.loads(request.body.decode('utf-8'))

            # Convert the data to a pandas DataFrame (assuming 'data' has the appropriate structure)
            dataframe = pd.DataFrame(data['previewData'])

            # Generate a unique order ID using the current timestamp
            order_id = f'ORDER-ID :- {timezone.now().strftime("%Y%m%d%H%M%S")}'

            # Convert DataFrame to a dictionary for JSON storage
            order_data_json = dataframe.to_dict(orient='records')

            # Create an Order object and save it to the database
            Order.objects.create(
                order_id=order_id,
                order_data=order_data_json,
                customer_email = request.user.email,
                customer_firstname = request.user.first_name,
                customer_lastname = request.user.last_name,
            )

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

            subject = f'New Order Received: {order_id}'
            message = 'Please find the attached Excel file containing the order details.'
            from_email = settings.EMAIL_HOST_USER
            cc_email = 'support10@pbkriscosales.net'
            recipient_list_with_cc = [request.user.email, cc_email]

            email = EmailMessage(subject, message, from_email, recipient_list_with_cc)
            email.attach('preview_order.xlsx', excel_buffer.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            email.send()

            excel_buffer.close()

            # Log the successful creation of the order
            logger.info(f'Order {order_id} created successfully.')

            # Return a success response with the order ID
            return JsonResponse({'success': True, 'order_id': order_id})

        except Exception as e:
            # Log the error
            logger.error(f'Error in SubmitPreviewView: {e}')

            # Return a response indicating failure
            return JsonResponse({'success': False, 'error': 'Failed to submit the order'})
        

        
class ThankYouView(View):
    template_name = 'thankyou.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


