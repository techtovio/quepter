# Generated by Django 3.2.19 on 2024-10-21 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='means',
        ),
        migrations.AddField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('Deposit', 'Deposit'), ('Withdrawal', 'Withdrawal'), ('Transfer', 'Transfer')], default='Deposit', max_length=20),
        ),
    ]
