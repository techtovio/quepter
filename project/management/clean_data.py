from django.core.management.base import BaseCommand
from project.models import Proposal, Club, Performance

class Command(BaseCommand):
    help = 'Collect and clean proposal and performance data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data collection...")

        proposals = Proposal.objects.all()
        for proposal in proposals:
            self.calculate_performance(proposal)

        self.stdout.write("Data collection complete.")

    def calculate_performance(self, proposal):
        performance = Performance.objects.get(proposal=proposal)
        
        # Example calculations
        success_rate = (performance.completion_time / proposal.timeline) * 100
        market_relevance = proposal.engagement_score * 0.1
        peer_score = proposal.peer_score * 0.2
        
        # Update performance model
        performance.success_rate = success_rate
        performance.market_relevance = market_relevance
        performance.save()
