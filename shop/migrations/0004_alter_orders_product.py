# Generated by Django 4.1.3 on 2022-12-30 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_alter_productlistings_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='product',
            field=models.ManyToManyField(blank=True, related_name='product', to='shop.orderproduct'),
        ),
    ]