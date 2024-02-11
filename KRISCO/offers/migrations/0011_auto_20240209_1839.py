# Generated by Django 3.1.4 on 2024-02-09 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0010_auto_20240205_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brandoffer',
            name='reason_for_offer_generation',
        ),
        migrations.AddField(
            model_name='brandoffer',
            name='customer_rank',
            field=models.CharField(choices=[('DIAMOND', 'DIAMOND'), ('PLATINUM', 'PLATINUM'), ('GOLD', 'GOLD'), ('SILVER', 'SILVER'), ('BRONZE', 'BRONZE'), ('IN HOME', 'INHOME')], default=' ', max_length=50),
            preserve_default=False,
        ),
    ]
