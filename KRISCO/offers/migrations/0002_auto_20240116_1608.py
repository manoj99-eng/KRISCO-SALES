# Generated by Django 3.1.4 on 2024-01-16 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weekly_offers',
            options={'ordering': ['brand', 'category', '-offer_price'], 'verbose_name': 'Weekly Offer', 'verbose_name_plural': 'Weekly Offers'},
        ),
        migrations.RenameField(
            model_name='weekly_offers',
            old_name='required_qunatity',
            new_name='required_quantity',
        ),
        migrations.AlterField(
            model_name='weekly_offers',
            name='discount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='weekly_offers',
            name='msrp',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='weekly_offers',
            name='offer_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='weekly_offers',
            name='sku',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]