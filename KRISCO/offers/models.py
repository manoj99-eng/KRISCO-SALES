from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User

product_category = (
    ("Haircare", "Haircare"),
    ("Skincare", "Skincare"),
    ("Makeup", "Makeup"),
    ("FMCG", "FMCG"),
    ("Accessories", "Accessories"),
)

class Weekly_Offer(models.Model):
    sku = models.CharField(max_length=200, unique=True)
    upc = models.BigIntegerField()
    description = models.CharField(max_length=600)
    brand = models.CharField(max_length=200)
    category = models.CharField(max_length=200, choices=product_category)
    available_qty = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    msrp = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    required_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Weekly Offer'
        verbose_name_plural = 'Weekly Offers'
        ordering = ['brand', 'category', '-offer_price']

    def __str__(self):
        return f"{self.brand} - {self.description} at ${self.offer_price}"

    def save(self, *args, **kwargs):
        # Calculate offer_price based on msrp and discount if they're not provided
        if not self.offer_price:
            self.offer_price = self.msrp - (self.msrp * (self.discount / Decimal('100.00')))
        super().save(*args, **kwargs)

CUSTOMER_RANK_CHOICES = (
    ('DIAMOND', 'DIAMOND'),
    ('PLATINUM', 'PLATINUM'),
    ('GOLD', 'GOLD'),
    ('SILVER', 'SILVER'),
    ('BRONZE','BRONZE'),
    ('IN HOME','INHOME')
    # Add more choices as needed
)
class BrandOffer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('SALON', 'SALON'),
        ('REGULAR', 'REGULAR'),
    ]
    date = models.DateField()
    time = models.TimeField()
    offer_type = models.CharField(max_length=7, choices=OFFER_TYPE_CHOICES)
    offer_file = models.FileField(upload_to='offers/brandoffer/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_person_first_name = models.CharField(max_length=255)
    created_person_last_name = models.CharField(max_length=255)
    created_person_email = models.EmailField()
    customer_rank = models.CharField(max_length=50, choices=CUSTOMER_RANK_CHOICES)

    def __str__(self):
        return f"{self.created_person_first_name} {self.created_person_last_name}'s Offer on {self.date}"
    class Meta:
        verbose_name = 'Brand Offer'
        verbose_name_plural = 'Brand Offers'


class EmailLog(models.Model):
    recipient_email = models.EmailField()
    cc_emails = models.TextField(blank=True, help_text="Comma-separated list of CC emails.")
    bcc_emails = models.TextField(blank=True, help_text="Comma-separated list of BCC emails.")
    subject = models.CharField(max_length=255)
    sent_attachment = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, help_text="Success or Failure")
    error_message = models.TextField(blank=True, help_text="Error message if sending failed.")

    def __str__(self):
        return f"{self.recipient_email} - {self.subject} - {'Sent' if self.status == 'Success' else 'Failed'}"