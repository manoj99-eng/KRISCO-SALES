# Generated by Django 3.1.4 on 2024-02-27 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_slides_slide_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrollingAdd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fontawsome_icon', models.CharField(max_length=400)),
                ('add_info_text', models.TextField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='slides',
            options={'verbose_name': 'Slides', 'verbose_name_plural': 'Slides'},
        ),
    ]