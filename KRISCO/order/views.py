from django.shortcuts import render
from django.http import HttpResponse
from .models import Order
import pandas as pd

def view_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order_data = order.order_data
        dataframe = pd.DataFrame(order_data)
        # Render the DataFrame as an HTML table
        return HttpResponse(dataframe.to_html())
    except Order.DoesNotExist:
        return HttpResponse('Order not found', status=404)