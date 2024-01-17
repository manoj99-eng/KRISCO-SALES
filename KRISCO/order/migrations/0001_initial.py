# Generated by Django 3.1.4 on 2024-01-17 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=100, unique=True)),
                ('order_data', models.JSONField()),
                ('customer_email', models.EmailField(max_length=254)),
                ('customer_firstname', models.CharField(max_length=100)),
                ('customer_lastname', models.CharField(max_length=100)),
                ('is_approved', models.BooleanField(default=False)),
            ],
        ),
    ]
