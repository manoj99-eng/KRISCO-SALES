from django.db import models
from multiselectfield import MultiSelectField
from staff.models import StaffEmailConfiguration
from django.core.exceptions import ValidationError

# Define choices for the dropdown fields
CUSTOMER_TYPE_CHOICES = (
    ('INTERNATIONAL', 'INTERNATIONAL'),
    ('MASS', 'MASS'),
    ('AMAZON SELLER', 'AMAZON SELLER'),
    ('RETAIL', 'RETAIL'),
    ('CLOSE OUTS', 'CLOSE OUTS'),
    ('HOME EMPLOYEE', 'HOME EMPLOYEE'),
    # Add more choices as needed
)

CUSTOMER_CATEGORY_CHOICES = (
    ('LUXURY', 'LUXURY'),
    ('MAKEUP', 'MAKEUP'),
    ('FMCG', 'FMCG'),
    ('HAIRCARE', 'HAIRCARE'),
    ('SKINCARE', 'SKINCARE'),
    # Add more choices as needed
)

CUSTOMER_RANK_CHOICES = (
    ('DIAMOND', 'DIAMOND'),
    ('PLATINUM', 'PLATINUM'),
    ('GOLD', 'GOLD'),
    ('SILVER', 'SILVER'),
    ('BRONZE', 'BRONZE'),
    ('IN HOME', 'INHOME'),
    # Add more choices as needed
)

class Customer(models.Model):
    customer_id = models.CharField(max_length=50, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mobile_extension = models.IntegerField()
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    customer_cc_email = models.TextField(null=True)
    customer_bcc_email = models.TextField(null=True)
    customer_type = models.CharField(max_length=50, choices=CUSTOMER_TYPE_CHOICES)
    customer_company = models.CharField(max_length=100)
    customer_category = MultiSelectField(choices=CUSTOMER_CATEGORY_CHOICES)
    customer_rank = models.CharField(max_length=50, choices=CUSTOMER_RANK_CHOICES)
    billing_address = models.TextField()
    shipping_address = models.TextField()
    staff_id = models.CharField(max_length=50)  # Using staff_id to store the identifier

    def __str__(self):
        return f"{self.customer_id} - {self.first_name} {self.last_name}"

    @property
    def staff(self):
        # Fetch the StaffEmailConfiguration instance based on staff_id
        try:
            return StaffEmailConfiguration.objects.get(staff_id=self.staff_id)
        except StaffEmailConfiguration.DoesNotExist:
            return None

    @property
    def customer_handler_first_name(self):
        # Dynamically fetch the handler's first name from StaffEmailConfiguration
        staff = self.staff
        return staff.first_name if staff else ''

    @property
    def customer_handler_last_name(self):
        # Dynamically fetch the handler's last name from StaffEmailConfiguration
        staff = self.staff
        return staff.last_name if staff else ''

    @property
    def customer_handler_email(self):
        # Dynamically fetch the handler's email from StaffEmailConfiguration
        staff = self.staff
        return staff.username if staff else ''

    def clean(self):
        # Ensure that staff_id corresponds to an existing StaffEmailConfiguration
        if self.staff_id and not StaffEmailConfiguration.objects.filter(staff_id=self.staff_id).exists():
            raise ValidationError({'staff_id': 'Invalid staff ID, staff does not exist.'})
        
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new instance
            prefix = f"{self.first_name[0]}{self.last_name[0]}"  # First letters of first and last name
            last_customer = Customer.objects.filter(customer_id__startswith=prefix).order_by('customer_id').last()
            if last_customer:
                sequence_num = int(last_customer.customer_id[2:-4]) + 1  # Extract and increment the sequence
            else:
                sequence_num = 1  # Start from 1 if no other customer is found
            self.customer_id = f"{prefix}{sequence_num:09}KSNJ"  # Format the customer_id
        super().save(*args, **kwargs)  # Call the super class's save method
