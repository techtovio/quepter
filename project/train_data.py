import os
import django
from decimal import Decimal

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quepter.settings')
django.setup()

from wallet.models import Proposal, Club
from django.contrib.auth.models import User

sample_proposals = [
    {
        'title': 'AI-Based Investment Platform',
        'description': 'An AI-powered platform that automates financial investments using predictive models.',
        'budget': Decimal(100000),
        'timeline': 90,
        'complexity': 0.8,
        'peer_score': 0.3,
        'engagement_score': 90,
        'club_success_rate': 0.75,
        'risk_level': 0.3,
        'proposer_reputation_score': 0.9,
        'status': 'approved',
        'outcome': 'success'
    },
    {
        'title': 'Community Solar Charging Station',
        'description': 'A solar-based phone charging station for rural communities.',
        'budget': Decimal(30000),
        'timeline': 60,
        'complexity': 0.6,
        'peer_score': 0.2,
        'engagement_score': 70,
        'club_success_rate': 0.65,
        'risk_level': 0.2,
        'proposer_reputation_score': 0.8,
        'status': 'approved',
        'outcome': 'success'
    },
    {
        'title': 'Decentralized Game Marketplace',
        'description': 'A marketplace where gamers can buy and sell in-game assets using blockchain.',
        'budget': Decimal(50000),
        'timeline': 120,
        'complexity': 0.9,
        'peer_score': 0.4,
        'engagement_score': 80,
        'club_success_rate': 0.5,
        'risk_level': 0.4,
        'proposer_reputation_score': 0.7,
        'status': 'pending',
        'outcome': 'in_progress'
    },
    {
        'title': 'Smart Health Diagnosis',
        'description': 'An AI-based system that analyzes patient symptoms to recommend diagnosis and treatments.',
        'budget': Decimal(150000),
        'timeline': 180,
        'complexity': 0.8,
        'peer_score': 0.5,
        'engagement_score': 95,
        'club_success_rate': 0.7,
        'risk_level': 0.5,
        'proposer_reputation_score': 0.85,
        'status': 'approved',
        'outcome': 'success'
    },
    {
        'title': 'AI-Powered Learning Hub',
        'description': 'A platform where students can learn coding and AI with interactive projects.',
        'budget': Decimal(80000),
        'timeline': 90,
        'complexity': 0.7,
        'peer_score': 0.3,
        'engagement_score': 85,
        'club_success_rate': 0.75,
        'risk_level': 0.3,
        'proposer_reputation_score': 0.85,
        'status': 'approved',
        'outcome': 'success'
    }
]

def seed_proposals():
    user = User.objects.first()
    club = Club.objects.first()

    if not user:
        print("❌ No users found. Create a user first.")
        return
    
    if not club:
        print("❌ No clubs found. Create a club first.")
        return

    for proposal_data in sample_proposals:
        proposal = Proposal.objects.create(
            title=proposal_data['title'],
            description=proposal_data['description'],
            budget=proposal_data['budget'],
            timeline=proposal_data['timeline'],
            complexity=proposal_data['complexity'],
            peer_score=proposal_data['peer_score'],
            engagement_score=proposal_data['engagement_score'],
            club=club,
            created_by=user,
            status=proposal_data['status']
        )
        proposal.outcome = proposal_data['outcome']
        proposal.save()
        print(f"✅ Created Proposal: {proposal.title}")

if __name__ == "__main__":
    seed_proposals()
