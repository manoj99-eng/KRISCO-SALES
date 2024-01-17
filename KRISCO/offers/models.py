from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

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
