from django.db import models
import json

class Order(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    order_data = models.JSONField()
    customer_email = models.EmailField()
    customer_firstname =models.CharField(max_length=100)
    customer_lastname =models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)
    notes = models.CharField(max_length=100, default ='3pl transaction number')

    def __str__(self):
        return self.order_id
