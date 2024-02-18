from django import forms
from django.template.defaultfilters import slugify
from customer.models import Customer, CUSTOMER_CATEGORY_CHOICES, CUSTOMER_RANK_CHOICES, CUSTOMER_TYPE_CHOICES
from customer.models import Customer

class DiscountForm(forms.Form):
    def __init__(self, unique_brands, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)

        for brand in unique_brands:
            field_name = slugify(brand)
            self.fields[f"discount_{field_name}"] = forms.DecimalField(
                label=f"{brand} Discount (%) :",
                required=True,
                min_value=0,
                max_value=100,
                widget=forms.NumberInput(attrs={'step': '0.01'})
            )

    def clean(self):
        cleaned_data = super().clean()
        for field_name, value in cleaned_data.items():
            try:
                cleaned_data[field_name] = float(value)  # Convert to float
            except (TypeError, ValueError):
                self.add_error(field_name, "Invalid input. Please enter a valid number.")
        return cleaned_data


class SalonDiscountForm(forms.Form):
    def __init__(self, unique_brands, *args, **kwargs):
        super(SalonDiscountForm, self).__init__(*args, **kwargs)

        # Create a discount field for each brand
        for brand in unique_brands:
            field_name = slugify(brand)
            self.fields[f"additional_discount_{field_name}"] = forms.DecimalField(
                label=f"{brand} Additional Discount (%) :",
                required=True,
                min_value=0,
                max_value=100,
                widget=forms.NumberInput(attrs={'step': '0.01'})
            )

    def clean(self):
        cleaned_data = super().clean()
        # Convert all input values to float and validate
        for field_name, value in cleaned_data.items():
            if value is not None:
                try:
                    cleaned_data[field_name] = float(value)
                except (TypeError, ValueError):
                    self.add_error(field_name, "Invalid input. Please enter a valid number.")
        return cleaned_data

class EditDiscountForm(forms.Form):

    display_qty = forms.IntegerField(
        label ='Display Qty',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    description = forms.CharField(
        label='Description',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cost = forms.DecimalField(
        label='Cost',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    discount = forms.DecimalField(
        label='Discount (%)',
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    offer_price = forms.DecimalField(
        label='Offer Price',
        max_digits=10,
        decimal_places=2,
        required=False,  # Not required because it's calculated based on cost and discount
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'})  # Read-only because it's calculated
    )

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get('cost')
        discount = cleaned_data.get('discount')
        
        # Calculate offer_price if both cost and discount are provided
        if cost is not None and discount is not None:
            offer_price = cost * (1 - discount / 100)
            cleaned_data['offer_price'] = round(offer_price, 2)  # Round to 2 decimal places

        return cleaned_data
    
class EditSalonDiscountForm(forms.Form):
    
    display_qty = forms.IntegerField(
        label ='Display Qty',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    description = forms.CharField(
        label='Description',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cost = forms.DecimalField(
        label='Cost',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    salon =forms.DecimalField(
        label = 'Salon',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    discount = forms.DecimalField(
        label='Discount (%)',
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    offer_price = forms.DecimalField(
        label='Offer Price',
        max_digits=10,
        decimal_places=2,
        required=False,  # Not required because it's calculated based on cost and discount
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'})  # Read-only because it's calculated
    )

    def clean(self):
        cleaned_data = super().clean()
        salon = cleaned_data.get('salon')
        discount = cleaned_data.get('discount')

        # Calculate offer_price if salon and discount are provided
        if salon is not None and discount is not None:
            offer_price = salon * (1 - discount / 100)
            cleaned_data['offer_price'] = round(offer_price, 2)  # Round to 2 decimal places
        return cleaned_data

class CustomerFilterForm(forms.Form):
    customer_rank = forms.MultipleChoiceField(choices=CUSTOMER_RANK_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    customer_type = forms.MultipleChoiceField(choices=CUSTOMER_TYPE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    customer_category = forms.MultipleChoiceField(choices=CUSTOMER_CATEGORY_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)


