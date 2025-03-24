# Generated by Django 3.2.19 on 2024-10-21 16:06

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=800)),
                ('image', models.ImageField(upload_to='events')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('description', models.TextField()),
                ('date', models.DateField()),
                ('is_completed', models.BooleanField(default=False)),
                ('location', models.CharField(max_length=255)),
            ],
        ),
    ]
