# order/urls.py

from django.urls import path
from . import views

app_name = 'order'  # Define the app namespace here

urlpatterns = [
    # ... your other urlpatterns
    path('order/<int:pk>/edit_json/', views.edit_order_json, name='edit_order_json'),
]
