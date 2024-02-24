from django.contrib import admin
from django.urls import path
from .views import WeeklyOffersView, AddToPreviewView, update_quantity_view, SubmitPreviewView, ThankYouView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('weekly-offers/', WeeklyOffersView.as_view(), name='weekly-offers'),
    path('weekly-offers/add-to-preview/', AddToPreviewView.as_view(), name='add-to-preview'),
    path('update-quantity/', update_quantity_view, name='update-quantity'),
    path('submit-preview/', SubmitPreviewView.as_view(), name='submit-preview'),  # Add this line
    path('thank-you/', ThankYouView.as_view(), name='thank-you'),

]