# Generated by Django 5.0.3 on 2025-06-17 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0003_remove_seller_account_age_months'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='median_trade_time',
        ),
        migrations.AddField(
            model_name='seller',
            name='online',
            field=models.BooleanField(default=False),
        ),
    ]
