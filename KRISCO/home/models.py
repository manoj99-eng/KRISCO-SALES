from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Max
from staff.models import StaffEmailConfiguration
# Create your models here.

class Brand(models.Model):
    brand_name = models.CharField(max_length=255, unique=True)
    brand_id = models.CharField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.brand_name

@receiver(pre_save, sender=Brand)
def pre_save_brand(sender, instance, *args, **kwargs):
    if not instance.brand_id:
        instance.brand_id = generate_brand_id(instance.brand_name)

def generate_brand_id(brand_name):
    if brand_name:
        base_id = f"{brand_name[0]}{brand_name[-1]}".upper()
        last_brand = Brand.objects.filter(brand_id__startswith=base_id).aggregate(max_id=Max('brand_id'))
        max_id = last_brand.get('max_id')

        if max_id:
            sequence_num = int(max_id[2:-4]) + 1  # Assuming the sequence is always at this position.
        else:
            sequence_num = 1

        new_id = f"{base_id}{str(sequence_num).zfill(7)}KSNJ"
        return new_id
    return None



class ContactUs(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"


class Team(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team_photos/')
    staff_configuration = models.ForeignKey(
        'staff.StaffEmailConfiguration',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    team_id = models.CharField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.team_id}"

# Signal to autofill team_id from StaffEmailConfiguration
@receiver(pre_save, sender=Team)
def autofill_team_id(sender, instance, **kwargs):
    if instance.staff_configuration and not instance.team_id:
        instance.team_id = instance.staff_configuration.staff_id


class Slides(models.Model):
    slide_label = models.CharField(max_length=200)
    slide_testmonial = models.TextField()
    slide_img = models.ImageField(upload_to='add_slides')
    class Meta:
        verbose_name = "Slides"
        verbose_name_plural = "Slides"

class ScrollingAdd(models.Model):
    fontawsome_icon = models.CharField(max_length=400)
    add_info_text = models.TextField()
    