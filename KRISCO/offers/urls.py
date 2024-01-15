from django.urls import path
from .views import *

urlpatterns = [
    path('weekly-offers/', WeeklyOffersView.as_view(), name='weekly-offers'),
    path('weekly-offers/add-to-preview/', AddToPreviewView.as_view(), name='add-to-preview'),
    path('update-quantity/', update_quantity_view, name='update-quantity'),
    path('submit-preview/', SubmitPreviewView.as_view(), name='submit-preview'),  # Add this line
    path('thank-you/', ThankYouView.as_view(), name='thank-you'),


]
