from django.core.management.base import BaseCommand
from wallet.ai import train_model

class Command(BaseCommand):
    help = 'Train the AI proposal scoring model'

    def handle(self, *args, **kwargs):
        model = train_model()
        if model:
            self.stdout.write(self.style.SUCCESS('✅ AI Model Trained Successfully'))
        else:
            self.stdout.write(self.style.ERROR('❌ No data available for training'))
