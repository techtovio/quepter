from django.core.management.base import BaseCommand
from app.models import Competition
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Run annual competition and select a winner'

    def handle(self, *args, **kwargs):
        current_year = now().year
        competition, created = Competition.objects.get_or_create(
            year=current_year,
            defaults={'prize_pool': 10000}  # Set a default prize pool in QPT
        )
        
        if not competition.winner:
            winner = competition.select_winner()
            if winner:
                self.stdout.write(self.style.SUCCESS(
                    f"Competition for {current_year} completed. Winner: {winner.title} (Club: {winner.club.name})"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"No eligible projects found for {current_year} competition."
                ))
        else:
            self.stdout.write(self.style.WARNING(
                f"Competition for {current_year} already has a winner."
            ))
