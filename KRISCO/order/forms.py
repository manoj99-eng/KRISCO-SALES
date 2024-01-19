from django import forms
from .models import Order

class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__' 