from django.urls import path
from . import views

urlpatterns = [
    path('<int:order_id>/view/', views.view_order, name='view_order'),
]