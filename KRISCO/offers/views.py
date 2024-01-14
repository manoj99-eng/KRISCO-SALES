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
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
from django.utils import timezone
import logging

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
        data = request.POST.getlist('data[]')
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

        # Perform the logic to update the quantity in the database based on the SKU
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
            # Get the JSON data from the request
            data = json.loads(request.body.decode('utf-8'))
            logger.info('Received data: %s', data)

            # Process the data, create a DataFrame
            dataframe = pd.DataFrame(data['previewData'])
            logger.info('DataFrame: %s', dataframe)

            # Convert DataFrame to Excel in-memory
            excel_buffer = BytesIO()
            dataframe.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)

            # Send email with Excel attachment
            subject = f'Preview Data - {timezone.now().strftime("%Y-%m-%d-%H:%M:%S")}'
            message = 'Please find the attached Excel file with your preview data.'
            from_email = settings.EMAIL_HOST_USER  # Update with your email
            recipient_list = [request.user.email]  # Assuming the user is logged in

            email = EmailMessage(subject, message, from_email, recipient_list)
            email.attach('preview_data.xlsx', excel_buffer.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            email.send()

            # Close the buffer to free up resources
            excel_buffer.close()

            # Return a JSON response with success and DataFrame data
            return JsonResponse({'success': True, 'dataframe': dataframe.to_dict(orient='records')})
        except Exception as e:
            logger.error('Error processing preview data: %s', str(e))
            return JsonResponse({'success': False, 'error': 'Failed to process preview data'})

class ThankYouView(View):
    template_name = 'thankyou.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
