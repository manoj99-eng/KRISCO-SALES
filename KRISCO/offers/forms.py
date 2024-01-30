from django import forms
from django.template.defaultfilters import slugify

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



class EditDiscountForm(forms.Form):
    new_discount = forms.DecimalField(
        label='New Discount',
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'step': 0.01})
    )
