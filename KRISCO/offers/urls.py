from django.urls import path
from .views import WeeklyOffersView, AddToPreviewView, update_quantity_view

urlpatterns = [
    path('weekly-offers/', WeeklyOffersView.as_view(), name='weekly-offers'),
    path('weekly-offers/add-to-preview/', AddToPreviewView.as_view(), name='add-to-preview'),
    path('update-quantity/', update_quantity_view, name='update-quantity'),  # Define the URL pattern
]
