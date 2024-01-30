from django.db import models
from django.utils import timezone

class Item(models.Model):
    CLASSIFICATION_CHOICES = [
        ('BAGS', 'BAGS'),
        ('BAKING SODA', 'BAKING SODA'),
        ('BELT', 'BELT'),
        ('BELTS', 'BELTS'),
        ('CANDLES', 'CANDLES'),
        ('DENTALCARE', 'DENTAL CARE'),
        ('DEODORANT', 'DEODORANT'),
        ('EAU PERFUMES', 'EAU PERFUMES'),
        ('EDC PERFUMES', 'EDC PERFUMES'),
        ('EDP PERFUMES', 'EDP PERFUMES'),
        ('EDT PERFUMES', 'EDT PERFUMES'),
        ('FRAGRANCE LOTION', 'FRAGRANCE LOTION'),
        ('FRAGRANCE MIST', 'FRAGRANCE MIST'),
        ('GLASSES', 'GLASSES'),
        ('GROOMING', 'GROOMING'),
        ('HAIR BRUSH', 'HAIR BRUSH'),
        ('HAIR STRAIGHTENER', 'HAIR STRAIGHTENER'),
        ('HAIRCARE', 'HAIRCARE'),
        ('HEALTHCARE', 'HEALTHCARE'),
        ('HOMECARE', 'HOMECARE'),
        ('JEWELRY', 'JEWELRY'),
        ('MAKEUP', 'MAKEUP'),
        ('MEDICATION', 'MEDICATION'),
        ('NAIL POLISH', 'NAIL POLISH'),
        ('PERFUMES', 'PERFUMES'),
        ('PERFUMES SET', 'PERFUMES SET'),
        ('PERSONAL CARE', 'PERSONAL CARE'),
        ('SAMPLE', 'SAMPLE'),
        ('SHOES', 'SHOES'),
        ('SKINCARE', 'SKINCARE'),
        ('TESTER', 'TESTER'),
        ('WATCH', 'WATCH'),
        ('WATER BOTTLES', 'WATER BOTTLES'),
    ]

    sku = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=600)
    brand = models.CharField(max_length=200)
    upc = models.CharField(max_length=200)
    unit_weight = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    classification = models.CharField(max_length=200, choices=CLASSIFICATION_CHOICES)
    notes = models.CharField(max_length=300, default='add your notes')

    def __str__(self):
        return f"{self.sku} - {self.description}"





class Stock(models.Model):
    CLASSIFICATION_CHOICES = [
        ('BAGS', 'BAGS'),
        ('BAKING SODA', 'BAKING SODA'),
        ('BELT', 'BELT'),
        ('BELTS', 'BELTS'),
        ('CANDLES', 'CANDLES'),
        ('DENTALCARE', 'DENTAL CARE'),
        ('DEODORANT', 'DEODORANT'),
        ('EAU PERFUMES', 'EAU PERFUMES'),
        ('EDC PERFUMES', 'EDC PERFUMES'),
        ('EDP PERFUMES', 'EDP PERFUMES'),
        ('EDT PERFUMES', 'EDT PERFUMES'),
        ('FRAGRANCE LOTION', 'FRAGRANCE LOTION'),
        ('FRAGRANCE MIST', 'FRAGRANCE MIST'),
        ('GLASSES', 'GLASSES'),
        ('GROOMING', 'GROOMING'),
        ('HAIR BRUSH', 'HAIR BRUSH'),
        ('HAIR STRAIGHTENER', 'HAIR STRAIGHTENER'),
        ('HAIRCARE', 'HAIRCARE'),
        ('HEALTHCARE', 'HEALTHCARE'),
        ('HOMECARE', 'HOMECARE'),
        ('JEWELRY', 'JEWELRY'),
        ('MAKEUP', 'MAKEUP'),
        ('MEDICATION', 'MEDICATION'),
        ('NAIL POLISH', 'NAIL POLISH'),
        ('PERFUMES', 'PERFUMES'),
        ('PERFUMES SET', 'PERFUMES SET'),
        ('PERSONAL CARE', 'PERSONAL CARE'),
        ('SAMPLE', 'SAMPLE'),
        ('SHOES', 'SHOES'),
        ('SKINCARE', 'SKINCARE'),
        ('TESTER', 'TESTER'),
        ('WATCH', 'WATCH'),
        ('WATER BOTTLES', 'WATER BOTTLES'),
    ]
    sku = models.CharField(max_length=200, unique=True)
    upc = models.CharField(max_length=200)
    item_classification = models.CharField(max_length=200, choices=CLASSIFICATION_CHOICES)
    description = models.CharField(max_length=600)
    on_hand = models.IntegerField()
    allocated = models.IntegerField(blank=True, null=True)
    available = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.sku} - {self.description}"

class InOutReport(models.Model):
    sku = models.CharField(max_length=200, unique=True)
    item_description = models.CharField(max_length=700)
    qty_in = models.PositiveIntegerField(default=0)
    qty_out = models.PositiveIntegerField(default=0)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.sku} - {self.item_description}"


class SlowMoversReport(models.Model):
    CLASSIFICATION_CHOICES = [
        ('BAGS', 'BAGS'),
        ('BAKING SODA', 'BAKING SODA'),
        ('BELT', 'BELT'),
        ('BELTS', 'BELTS'),
        ('CANDLES', 'CANDLES'),
        ('DENTALCARE', 'DENTAL CARE'),
        ('DEODORANT', 'DEODORANT'),
        ('EAU PERFUMES', 'EAU PERFUMES'),
        ('EDC PERFUMES', 'EDC PERFUMES'),
        ('EDP PERFUMES', 'EDP PERFUMES'),
        ('EDT PERFUMES', 'EDT PERFUMES'),
        ('FRAGRANCE LOTION', 'FRAGRANCE LOTION'),
        ('FRAGRANCE MIST', 'FRAGRANCE MIST'),
        ('GLASSES', 'GLASSES'),
        ('GROOMING', 'GROOMING'),
        ('HAIR BRUSH', 'HAIR BRUSH'),
        ('HAIR STRAIGHTENER', 'HAIR STRAIGHTENER'),
        ('HAIRCARE', 'HAIRCARE'),
        ('HEALTHCARE', 'HEALTHCARE'),
        ('HOMECARE', 'HOMECARE'),
        ('JEWELRY', 'JEWELRY'),
        ('MAKEUP', 'MAKEUP'),
        ('MEDICATION', 'MEDICATION'),
        ('NAIL POLISH', 'NAIL POLISH'),
        ('PERFUMES', 'PERFUMES'),
        ('PERFUMES SET', 'PERFUMES SET'),
        ('PERSONAL CARE', 'PERSONAL CARE'),
        ('SAMPLE', 'SAMPLE'),
        ('SHOES', 'SHOES'),
        ('SKINCARE', 'SKINCARE'),
        ('TESTER', 'TESTER'),
        ('WATCH', 'WATCH'),
        ('WATER BOTTLES', 'WATER BOTTLES'),
    ]
    report_date = models.DateField(default=timezone.now)
    sku = models.CharField(max_length=200, unique=True)
    upc = models.CharField(max_length=200)
    brand =models.CharField(max_length=300)
    item_classification = models.CharField(max_length=200,choices=CLASSIFICATION_CHOICES)
    description = models.CharField(max_length=700)
    qtyin_oneyear = models.IntegerField()
    qtyout_oneyear = models.IntegerField()
    balance_oneyear = models.IntegerField()
    available = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    begining_balance = models.IntegerField()
    reference = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    sellercategory = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.report_date} - {self.sku} - {self.description}"

    class Meta:
        verbose_name = 'Slow Mover Report'
        verbose_name_plural = 'Slow Movers Reports'
        unique_together = ('report_date', 'sku')