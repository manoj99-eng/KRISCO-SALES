import os
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.contrib import messages
from django.db import transaction
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.core.files import File
from django.utils.http import urlquote
from urllib.request import urlopen
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from io import BytesIO
from .models import *
import csv
import logging

logger = logging.getLogger(__name__)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_id', 'brand_name', 'image_preview')  # Adjust as per your model fields
    search_fields = ['brand_id', 'brand_name']
    actions = ['download_csv_template']

    def image_preview(self, obj):
        if obj.image:  # Make sure to use the correct field name here
            return format_html('<img src="{}" style="width: 150px; height: auto;" />', obj.image.url)
        return "No Image Uploaded"
    image_preview.short_description = 'Image Preview'


    def download_csv_template(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="brand_template.csv"'
        writer = csv.writer(response)
        headers = ['brand_name', 'image']  # Assuming these are the fields you want to include
        writer.writerow(headers)
        return response
    download_csv_template.short_description = "Download CSV template for Brands"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='import-csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
            if request.method == 'POST':
                csv_file = request.FILES.get('csv_file')

                if not csv_file or not csv_file.name.endswith('.csv'):
                    messages.error(request, 'The wrong file type was uploaded. Please upload a CSV file.')
                    return HttpResponseRedirect(request.path_info)

                try:
                    decoded_file = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    with transaction.atomic():
                        for row in reader:
                            brand_name = row.get('brand_name')
                            image_path = row.get('image')  # Get the image path from the CSV
                            
                            # Create a new Brand object
                            brand, created = Brand.objects.get_or_create(
                                brand_name=brand_name,
                            )
                            
                            # Handle image upload if the path is provided
                            if image_path:
                                # Construct the full local file path
                                full_file_path = os.path.join(settings.MEDIA_ROOT, image_path)
                                
                                # Open the image file
                                with open(full_file_path, 'rb') as image_file:
                                    brand.image.save(os.path.basename(image_path), ContentFile(image_file.read()), save=True)
                            
                            # Save the Brand object
                            brand.save()

                        messages.success(request, 'CSV file has been imported successfully!')
                except Exception as e:
                            messages.error(request, 'Something went wrong: ' + str(e))
                            return HttpResponseRedirect(request.path_info)

                # For GET requests, show a simple upload form
            return render(request, 'admin/import_csv.html')


# Define a custom admin class
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'short_message')  # Fields to be displayed in the admin list
    search_fields = ('first_name', 'last_name', 'email', 'message')  # Fields to be searchable
    list_filter = ('first_name','email')  # Fields to add a filter for
    readonly_fields = ('message',)

    def short_message(self, obj):
        return obj.message[:50]  # Display the first 50 characters of the message

    short_message.short_description = 'Message'  # Column header for the message

# Register the admin class with the associated model
admin.site.register(ContactUs, ContactUsAdmin)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'title', 'team_id', 'staff_configuration_link', 'photo_preview')
    search_fields = ('first_name', 'last_name', 'title', 'team_id', 'staff_configuration__staff_id')
    list_filter = ('title',)
    raw_id_fields = ('staff_configuration',)

    def staff_configuration_link(self, obj):
        if obj.staff_configuration:
            return obj.staff_configuration.staff_id
        return None
    staff_configuration_link.short_description = 'Staff Configuration'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 150px; height: auto;" />', obj.photo.url)
        return ""
    photo_preview.short_description = 'Photo Preview'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('staff_configuration')
        return queryset
    

class SlidesAdmin(admin.ModelAdmin):
    list_display = ('slide_label', 'short_testimonial', 'image_preview')  # Columns to display
    search_fields = ('slide_label', 'slide_testmonial')  # Fields that can be searched
    
    def short_testimonial(self, obj):
        return obj.slide_testmonial[:50] + '...' if len(obj.slide_testmonial) > 50 else obj.slide_testmonial
    short_testimonial.short_description = 'Testimonial'

    def image_preview(self, obj):
        return mark_safe('<img src="{}" width="150" height="auto" />'.format(obj.slide_img.url)) if obj.slide_img else ''
    image_preview.short_description = 'Image Preview'

admin.site.register(Slides, SlidesAdmin)

admin.site.register(ScrollingAdd)