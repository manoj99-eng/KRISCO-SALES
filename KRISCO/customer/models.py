from django.db import models
from multiselectfield import MultiSelectField

# Define choices for the dropdown fields
CUSTOMER_TYPE_CHOICES = (
    ('INTERNATIONAL', 'INTERNATIONAL'),
    ('MASS', 'MASS'),
    ('AMAZON SELLER', 'AMAZON SELLER'),
    ('RETAIL', 'RETAIL'),
    ('CLOSE OUTS','CLOSE OUTS'),
    ('HOME EMPLOYEE','HOME EMPLOYEE')
    # Add more choices as needed
)

CUSTOMER_CATEGORY_CHOICES = (
    ('LUXURY', 'LUXURY'),
    ('MAKEUP', 'MAKEUP'),
    ('FMCG', 'FMCG'),
    ('HAIRCARE','HAIRCARE'),
    ('SKINCARE','SKINCARE'),
    # Add more choices as needed
)

CUSTOMER_RANK_CHOICES = (
    ('DIAMOND', 'DIAMOND'),
    ('PLATINUM', 'PLATINUM'),
    ('GOLD', 'GOLD'),
    ('SILVER', 'SILVER'),
    ('BRONZE','BRONZE'),
    ('IN HOME','INHOME')
    # Add more choices as needed
)

class Customer(models.Model):
    customer_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mobile_extension = models.IntegerField()
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    customer_type = models.CharField(max_length=50, choices=CUSTOMER_TYPE_CHOICES)
    customer_company = models.CharField(max_length=100)
    customer_category = MultiSelectField(choices=CUSTOMER_CATEGORY_CHOICES)
    customer_rank = models.CharField(max_length=50, choices=CUSTOMER_RANK_CHOICES)
    billing_address = models.TextField()
    shipping_address = models.TextField()
    handler_first_name = models.CharField(max_length=100)
    handler_last_name = models.CharField(max_length=100)
    handler_email = models.EmailField()

    def __str__(self):
        return f"{self.customer_id} - {self.first_name} {self.last_name}"
