from django.db import models

product_category =(("Haircare","Haircare"),("Skincare","Skincare"),("Makeup", "Makeup"),("FMCG","FMCG"),("Accessories","Accessories"))

# Create your models here.
class Weekly_Offers(models.Model):
    sku = models.CharField(max_length=200)
    upc = models.BigIntegerField()
    description = models.CharField(max_length=600)
    brand = models.CharField(max_length=200)
    category =models.CharField(max_length=200, choices= product_category)
    available_qty = models.IntegerField()
    msrp =models.FloatField()
    discount =models.FloatField()
    offer_price =models.FloatField()
    required_qunatity =models.IntegerField()


