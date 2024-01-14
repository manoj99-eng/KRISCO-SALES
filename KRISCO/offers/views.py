from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db import models
import pandas as pd
from .models import Weekly_Offers

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
