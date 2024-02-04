from io import StringIO
import json
from django.urls import path,reverse
from django.contrib import admin
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
import pandas as pd
from .models import Weekly_Offer, BrandOffer
import csv
from django.db.models import Q
import logging
from django.contrib import messages
from inventory.models import SlowMoversReport
from .forms import DiscountForm,EditDiscountForm
from django.template.defaultfilters import slugify
from django.http import JsonResponse

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



logger = logging.getLogger(__name__)
@admin.register(BrandOffer)
class BrandOfferAdmin(admin.ModelAdmin):
    list_display = ['sku', 'description', 'available', 'cost', 'discount', 'offer_price']
    list_filter = ['discount']  # Add more fields to filter as needed
    search_fields = ['sku', 'description']  # Add more fields to search as needed

    actions = ['generate_offers']

    def edit_discount_item(self, request, sku):
        response_data = {'success': False, 'message': '', 'data': {}}
        try:
            filtered_data_df_json = request.session.get('filtered_data_df')
            if not filtered_data_df_json:
                response_data['message'] = 'Session data not found.'
                return JsonResponse(response_data)

            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')
            if sku not in df['sku'].values:
                response_data['message'] = 'Item not found.'
                return JsonResponse(response_data)

            if request.method == 'POST':
                form = EditDiscountForm(request.POST)
                if form.is_valid():
                    idx = df.index[df['sku'] == sku].tolist()[0]
                    df.at[idx, 'description'] = form.cleaned_data['description']
                    df.at[idx, 'cost'] = float(form.cleaned_data['cost'])
                    df.at[idx, 'discount'] = float(form.cleaned_data['discount'])
                    df.at[idx, 'offer_price'] = round(float(form.cleaned_data['cost']) * (1 - float(form.cleaned_data['discount']) / 100), 2)

                    request.session['filtered_data_df'] = df.to_json(orient='split')
                    response_data['success'] = True
                    response_data['message'] = 'Item updated successfully.'
                    return JsonResponse(response_data)
                else:
                    response_data['message'] = 'Form validation error.'
                    return JsonResponse(response_data)
            else:
                response_data['message'] = 'Invalid request method.'
                return JsonResponse(response_data)
        except Exception as e:
            response_data['message'] = f'An error occurred: {str(e)}'
            return JsonResponse(response_data)
        
    def remove_discount_item(self, request, sku):
        try:
            filtered_data_df_json = request.session.get('filtered_data_df')
            if not filtered_data_df_json:
                messages.error(request, 'Session data not found.')
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')
            
            # Logic to remove item based on sku
            df = df[df['sku'] != sku]
            request.session['filtered_data_df'] = df.to_json(orient='split')

            messages.success(request, 'Item removed successfully.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    def offer_discount(self, request):
        context = {}
        filtered_data_df_json = request.session.get('filtered_data_df')
        if filtered_data_df_json:
            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')
            unique_brands = sorted(df['brand'].unique().tolist())
        else:
            unique_brands = []  # Fallback if there's no DataFrame data

        if request.method == 'POST':
            form = DiscountForm(unique_brands, request.POST)  # Initialize form with unique brands
            if form.is_valid():
                cleaned_data = form.cleaned_data
                if filtered_data_df_json:
                    # Loop through each dynamically created field and apply the discount
                    for brand in unique_brands:
                        field_name = f"discount_{slugify(brand)}"
                        discount_rate = cleaned_data.get(field_name, 0) / 100
                        # Round the discount rate to 2 decimals and apply it
                        df.loc[df['brand'] == brand, 'discount'] = round(discount_rate * 100, 2)  # Store as a percentage, rounded
                        df.loc[df['brand'] == brand, 'offer_price'] = (df['cost'] * (1 - discount_rate)).round(2)
                    # Save the updated DataFrame back to the session
                    request.session['filtered_data_df'] = df.to_json(orient='split')
                    context['df'] = df.to_dict(orient='records')  # Prepare data for template rendering
                else:
                    context['error'] = 'No data found to apply discounts to.'
            else:
                context['form'] = form
        else:
            form = DiscountForm(unique_brands)  # Initialize form with 'unique_brands' for GET requests
            context['form'] = form

            # Prepare existing DataFrame data for template rendering, if available
            if filtered_data_df_json:
                context['df'] = df.to_dict(orient='records')

        return render(request, 'admin/offers/brandoffer/offer_discount.html', context)

    @staticmethod
    def offer_edit(request):
        # This method needs to be able to handle the request object directly
        if 'filtered_data_df' in request.session:
            filtered_data_df_json = request.session['filtered_data_df']
            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')

            # Prepare your context with the DataFrame
            context = {'df': df.to_dict(orient='records')}
            return render(request, 'admin/offers/brandoffer/offer_edit.html', context)
        else:
            # If no DataFrame is found in the session, redirect or show an error
            messages.error(request, "No data found in session.")
            return redirect('admin:index')  # Adjust the redirect as needed

    def generate_offers(self, request, queryset):
        # Retrieve selected filters from session storage
        selected_filters_json = request.session.get('selectedFilters')
        selected_filters = json.loads(selected_filters_json) if selected_filters_json else {}

        value = SlowMoversReport.objects.all()
        unique_brands = sorted(set(record.brand for record in value))
        unique_sellercategories = sorted(set(record.sellercategory for record in value))

        # Store selected brands in session
        selected_filters['selected_brands'] = request.POST.getlist('brand', [])
        request.session['selectedFilters'] = json.dumps(selected_filters)

        return render(request, 'admin/offers/brandoffer/offer_generation.html', {'unique_brands': unique_brands, 'unique_sellercategories': unique_sellercategories, 'selected_filters': selected_filters})

    def filter_offers(self, request, queryset=None):
            if request.method == 'POST':
                sellercategory = request.POST.getlist('sellercategory', [])
                brands = request.POST.getlist('brand', [])

                # Create a list to hold the brand filters
                brand_filters = []

                # Loop through selected brands and create a Q object for each
                for selected_brand in brands:
                    brand_filter = Q(brand__startswith=selected_brand)
                    brand_filters.append(brand_filter)

                # Combine the brand filters using the | operator
                combined_brand_filters = Q()
                for brand_filter in brand_filters:
                    combined_brand_filters |= brand_filter

                # Filter records based on user input and exclude records where 'available' is 0
                filtered_data = SlowMoversReport.objects.filter(
                    Q(sellercategory__in=sellercategory),
                    combined_brand_filters,
                    available__gt=0  # Greater than 0
                )

                # Create a DataFrame 'df' from the 'filtered_data'
                df = pd.DataFrame(list(filtered_data.values()))
                # Store the DataFrame in the session
                request.session['filtered_data_df'] = df.to_json(orient='split')

                # Render the filtered data in a new template
                return render(request, 'admin/offers/brandoffer/filtered_data.html', {'filtered_data': filtered_data})

            return render(request, 'admin/offers/brandoffer/offer_generation.html', {'value': queryset})

    generate_offers.short_description = 'Generate Offers'
    filter_offers.short_description = 'Filter Offers'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_offers/', self.admin_site.admin_view(self.generate_offers), name='generate_offers'),
            path('filter_offers/', self.admin_site.admin_view(self.filter_offers), name='filter_offers'),
            path('offer_discount/', self.admin_site.admin_view(self.offer_discount), name='offer_discount'),
            path('offer_edit/', self.admin_site.admin_view(self.offer_edit), name='admin_offer_edit'),  # Added trailing slash
            path('offer_edit/edit/<str:sku>/', self.admin_site.admin_view(self.edit_discount_item), name='edit_discount_item'),  # Wrapped with admin_view
            path('offer_edit/remove/<str:sku>/', self.admin_site.admin_view(self.remove_discount_item), name='remove_discount_item'),  # Wrapped with admin_view
        ]
        return custom_urls + urls
