from urllib import request
from django.contrib import admin, messages
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
import pandas as pd
from .models import *
from offers.models import Weekly_Offer
import json
from django.utils.html import format_html
from django.contrib import messages


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_email', 'customer_firstname', 'customer_lastname', 'is_approved', 'notes',)
    readonly_fields = ('order_id', 'order_data_pretty', 'customer_email', 'customer_firstname', 'customer_lastname',)
    exclude = ('order_data',)
    search_fields = ['order_id', 'customer_email', 'customer_firstname', 'customer_lastname']

    actions = ['approve_orders']

    def order_data_pretty(self, instance):
        try:
            # Convert the JSON data to a Python object
            if isinstance(instance.order_data, str):
                try:
                    data = json.loads(instance.order_data)  # Load it as JSON
                except json.JSONDecodeError:
                    return 'Invalid JSON format'
            else:
                data = instance.order_data 
            
            # Begin the HTML table
            html = '<table class="table">'
            
            # Create the table header
            html += ('<thead>'
                     '<tr>'
                     '<th>SKU</th>'
                     '<th>UPC</th>'
                     '<th>Description</th>'
                     '<th>Entered Quantity</th>'
                     '<th>Offered Price</th>'
                     '</tr>'
                     '</thead>')
            
            # Loop through the data items and create table rows
            for item in data:
                html += '<tr>'
                html += f"<td>{item.get('sku', '')}</td>"
                html += f"<td>{item.get('upc', '')}</td>"
                html += f"<td>{item.get('description', '')}</td>"
                html += f"<td>{item.get('entered_quantity', '')}</td>"
                html += f"<td>{item.get('offered_price', '')}</td>"
                html += '</tr>'
            
            html += '</table>'
            return format_html(html)
        
        except json.JSONDecodeError:
            return 'Invalid JSON format'

    order_data_pretty.short_description = "Order Data"

    def approve_orders(self, request, queryset):
        # Process the queryset to approve orders
        for order in queryset:
            self.update_weekly_offer_quantities(order, subtract=True)
            order.is_approved = True
            order.save()
        messages.success(request, "Selected orders have been approved and quantities updated.")

    approve_orders.short_description = 'Approve selected orders'

    actions = [approve_orders]

    def save_model(self, request, obj, form, change):
        # Determine if we are approving or unapproving
        is_approving = 'is_approved' in form.changed_data and obj.is_approved
        is_unapproving = 'is_approved' in form.changed_data and not obj.is_approved

        super().save_model(request, obj, form, change)

        # If there's a change in the 'is_approved' status, update quantities
        if is_approving or is_unapproving:
            self.update_weekly_offer_quantities(obj, subtract=is_approving)

    from django.contrib import messages

    def update_weekly_offer_quantities(self, request, order, subtract):
        try:
            for item in order.order_data:
                sku = item.get('sku')
                quantity = item.get('entered_quantity')
                weekly_offer = Weekly_Offer.objects.get(sku=sku)
                if subtract:
                    if weekly_offer.available_qty >= quantity:
                        weekly_offer.available_qty -= quantity
                        weekly_offer.save()
                    else:
                        messages.error(request, f"Not enough quantity for SKU {sku}.", extra_tags='danger')
                        break  # Break out of the loop on error, no further processing
                else:
                    weekly_offer.available_qty += quantity
                    weekly_offer.save()
            else:
                # No errors occurred, approve the order and redirect
                order.is_approved = True
                order.save()
                messages.success(request, "Order has been successfully approved and quantities updated.", extra_tags='success')
                return True  # Returning True to indicate success
        except Weekly_Offer.DoesNotExist:
            messages.error(request, f"Weekly offer with SKU {sku} does not exist.", extra_tags='danger')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')

        # Returning False to indicate error
        return False

    def save_model(self, request, obj, form, change):
        if 'is_approved' in form.changed_data:
            # Determine if we are approving or unapproving
            is_approving = obj.is_approved
            if is_approving:
                success = self.update_weekly_offer_quantities(request, obj, subtract=is_approving)
                if not success:
                    # If there was an error, keep the is_approved status unchanged
                    obj.is_approved = not is_approving
            else:
                # For unapproving, simply reverse the quantities
                self.update_weekly_offer_quantities(request, obj, subtract=is_approving)

        super().save_model(request, obj, form, change)


    approve_orders.short_description = 'Approve selected orders'