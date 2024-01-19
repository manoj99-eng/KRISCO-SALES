from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from .models import Order
from offers.models import Weekly_Offer
import json

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_email', 'customer_firstname', 'customer_lastname', 'is_approved', 'notes', 'edit_json_link')
    readonly_fields = ('order_id', 'order_data_pretty', 'customer_email', 'customer_firstname', 'customer_lastname')
    exclude = ('order_data',)
    search_fields = ['order_id', 'customer_email', 'customer_firstname', 'customer_lastname']
    actions = ['approve_orders']

    def edit_json_link(self, obj):
        if obj.is_approved:
            return format_html('<span>Editing Disabled</span>')
        else:
            link = reverse('order:edit_order_json', args=[obj.pk])
            return format_html('<a href="{}">Edit Order</a>', link)
    edit_json_link.short_description = 'Edit Customer Order'

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
        for order in queryset:
            self.update_weekly_offer_quantities(request, order, subtract=True)
            order.is_approved = True
            order.save()
        messages.success(request, "Selected orders have been approved and quantities updated.")
    approve_orders.short_description = 'Approve selected orders'

    def save_model(self, request, obj, form, change):
        # Save the object first
        super().save_model(request, obj, form, change)

        # Check if 'is_approved' has been changed
        is_approving = 'is_approved' in form.changed_data and obj.is_approved
        is_unapproving = 'is_approved' in form.changed_data and not obj.is_approved

        # Update quantities based on the approval status
        if is_approving or is_unapproving:
            # Call the method to update quantities and handle success or failure
            success = self.update_weekly_offer_quantities(request, obj, subtract=is_approving)
            if not success and is_approving:
                # If there was an error in updating quantities, revert the is_approved change
                obj.is_approved = False
                obj.save(update_fields=['is_approved'])
                # Optionally, you can add a message to inform the admin user
                messages.error(request, "Failed to approve order due to insufficient quantities.")



    def update_weekly_offer_quantities(self, request, order, subtract):
            try:
                for item in order.order_data:
                    sku = item.get('sku')
                    quantity = item.get('entered_quantity')
                    weekly_offer = Weekly_Offer.objects.get(sku=sku)
                    if subtract:
                        if weekly_offer.available_qty >= quantity:
                            weekly_offer.available_qty -= quantity
                        else:
                            messages.error(request, f"Not enough quantity for SKU {sku}.", extra_tags='danger')
                            return False
                    else:
                        weekly_offer.available_qty += quantity
                    weekly_offer.save()
                return True
            except Weekly_Offer.DoesNotExist:
                messages.error(request, f"Weekly offer with SKU {sku} does not exist.", extra_tags='danger')
                return False
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
                return False

