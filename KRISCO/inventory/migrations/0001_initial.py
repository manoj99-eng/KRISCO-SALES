# Generated by Django 3.1.4 on 2024-01-25 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=200, unique=True)),
                ('description', models.CharField(max_length=500)),
                ('brand', models.CharField(max_length=200)),
                ('upc', models.BigIntegerField()),
                ('unit_weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('classification', models.CharField(choices=[('BAGS', 'BAGS'), ('BAKING SODA', 'BAKING SODA'), ('BELT', 'BELT'), ('BELTS', 'BELTS'), ('CANDLES', 'CANDLES'), ('DENTALCARE', 'DENTAL CARE'), ('DEODORANT', 'DEODORANT'), ('EAU PERFUMES', 'EAU PERFUMES'), ('EDC PERFUMES', 'EDC PERFUMES'), ('EDP PERFUMES', 'EDP PERFUMES'), ('EDT PERFUMES', 'EDT PERFUMES'), ('FRAGRANCE LOTION', 'FRAGRANCE LOTION'), ('FRAGRANCE MIST', 'FRAGRANCE MIST'), ('GLASSES', 'GLASSES'), ('GROOMING', 'GROOMING'), ('HAIR BRUSH', 'HAIR BRUSH'), ('HAIR STRAIGHTENER', 'HAIR STRAIGHTENER'), ('HAIRCARE', 'HAIRCARE'), ('HEALTHCARE', 'HEALTHCARE'), ('HOMECARE', 'HOMECARE'), ('JEWELRY', 'JEWELRY'), ('MAKEUP', 'MAKEUP'), ('MEDICATION', 'MEDICATION'), ('NAIL POLISH', 'NAIL POLISH'), ('PERFUMES', 'PERFUMES'), ('PERFUMES SET', 'PERFUMES SET'), ('PERSONAL CARE', 'PERSONAL CARE'), ('SAMPLE', 'SAMPLE'), ('SHOES', 'SHOES'), ('SKINCARE', 'SKINCARE'), ('TESTER', 'TESTER'), ('WATCH', 'WATCH'), ('WATER BOTTLES', 'WATER BOTTLES')], max_length=200)),
                ('notes', models.CharField(default='add your notes', max_length=300)),
            ],
        ),
    ]
