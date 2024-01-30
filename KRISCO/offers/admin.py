from io import StringIO
import json
from django.urls import path,reverse
from django.contrib import admin
from django.shortcuts import render
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


@admin.register(BrandOffer)
class BrandOfferAdmin(admin.ModelAdmin):
    list_display = ['sku', 'description', 'available', 'cost', 'discount', 'offer_price']
    list_filter = ['discount']  # Add more fields to filter as needed
    search_fields = ['sku', 'description']  # Add more fields to search as needed

    actions = ['generate_offers']

    def edit_discount_item(self, request, item_id):
        # Retrieve the DataFrame from the session
        filtered_data_df_json = request.session.get('filtered_data_df')
        if filtered_data_df_json:
            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')
        else:
            df = None

        # Find the item in the DataFrame by `item_id`
        item_index = df[df.index == item_id].index[0]

        if request.method == 'POST':
            form = EditDiscountForm(request.POST)
            if form.is_valid():
                # Update the item with new data from the request
                new_discount = form.cleaned_data.get('new_discount', 0.0)
                df.at[item_index, 'discount'] = new_discount

                # Recalculate the offer price
                df.at[item_index, 'offer_price'] = df.at[item_index, 'cost'] * (1 - new_discount / 100)
                df.at[item_index, 'offer_price'] = round(df.at[item_index, 'offer_price'], 2)

                # Save the updated DataFrame back to the session
                updated_df_json = df.to_json(orient='split')
                request.session['filtered_data_df'] = updated_df_json

                # Return a JSON response indicating success
                return JsonResponse({'success': True})
            else:
                # Return a JSON response indicating form errors
                return JsonResponse({'success': False, 'errors': form.errors})
        else:
            # Return an appropriate response for rendering the edit form
            return render(request, 'admin/offers/brandoffer/edit_discount_item.html', {'item_id': item_id})

    def remove_discount_item(self, request, item_id):
        # Retrieve the DataFrame from the session
        filtered_data_df_json = request.session.get('filtered_data_df')
        if filtered_data_df_json:
            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')
        else:
            df = None

        # Remove the item from the DataFrame by `item_id`
        df.drop(item_id, inplace=True)

        # Save the updated DataFrame back to the session
        updated_df_json = df.to_json(orient='split')
        request.session['filtered_data_df'] = updated_df_json

        # Return a JSON response indicating success
        return JsonResponse({'success': True})


    def offer_discount(self, request):
        # Retrieve the DataFrame from the session
        filtered_data_df_json = request.session.get('filtered_data_df')
        if filtered_data_df_json:
            df = pd.read_json(StringIO(filtered_data_df_json), orient='split')
        else:
            df = None

        # Initialize unique_brands to an empty list by default
        unique_brands = df['brand'].unique() if df is not None and not df.empty else []

        if request.method == 'POST':
            form = DiscountForm(unique_brands, request.POST)
            if form.is_valid():
                # Process the form data
                discounts = {brand: form.cleaned_data.get(f"discount_{slugify(brand)}", 0.0) for brand in unique_brands}

                # Apply discounts to the DataFrame
                if df is not None:
                    for brand, discount in discounts.items():
                        df.loc[df['brand'] == brand, 'discount'] = discount

                    df['discount'] = df['discount'].astype(float)
                    df['offer_price'] = df['cost'] * (1 - df['discount'] / 100)
                    df['offer_price'] = df['offer_price'].round(2)
                    df['cost'] = df['cost'].round(2)

                    # Save the updated DataFrame back to the session
                    updated_df_json = df.to_json(orient='split')
                    request.session['filtered_data_df'] = updated_df_json
                    discounts_applied = True
                else:
                    discounts_applied = False
            else:
                discounts_applied = False
        else:
            form = DiscountForm(unique_brands)
            discounts_applied = False

        context = {
            'form': form,
            'unique_brands': unique_brands,
            'discounts_applied': discounts_applied,
            'df': df if df is not None and not df.empty else None,
        }
        return render(request, 'admin/offers/brandoffer/offer_discount.html', context)



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
            path('offer_discount/edit/<int:item_id>/', self.admin_site.admin_view(self.edit_discount_item), name='edit_discount_item'),
            path('offer_discount/remove/<int:item_id>/', self.admin_site.admin_view(self.remove_discount_item), name='remove_discount_item'),
    
        ]
        return custom_urls + urls