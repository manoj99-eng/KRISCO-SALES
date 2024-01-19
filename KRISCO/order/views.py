from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Order
import json

def edit_order_json(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        try:
            json_data = json.loads(request.POST.get('json_data'))
            order.order_data = json_data
            order.save()
            messages.success(request, 'Order data updated successfully.')
            return redirect('admin:order_order_change', object_id=order.pk)
        except json.JSONDecodeError as e:
            messages.error(request, f'Invalid JSON: {e}')

    context = {
        'order': order,
        'json_data': json.dumps(order.order_data, indent=4)
    }
    return render(request, 'admin/order/edit_order_json.html', context)

