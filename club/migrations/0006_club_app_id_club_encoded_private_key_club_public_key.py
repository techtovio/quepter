# Generated by Django 5.1.7 on 2025-03-27 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_club_qpt_wallet_balance_clubtransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='app_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='club',
            name='encoded_private_key',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='public_key',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
