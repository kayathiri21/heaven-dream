# Generated by Django 5.0.1 on 2024-03-21 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_alter_product_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('COD', 'Cash on Delivery'), ('upi', 'upi'), ('card', 'Credit/Debit Card')], max_length=10),
        ),
    ]
