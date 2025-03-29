from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Profile
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from uuid import uuid4
from django.utils import timezone
from datetime import datetime, timedelta
from uuid import uuid4
import uuid
from club.models import Club
from .ai import AIProposal, evaluate_proposal, calculate_score, generate_feedback_report
def gen_uuid():
    return uuid4()

  
class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]

    OUTCOME_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('in_progress', 'In Progress')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    timeline = models.IntegerField(help_text="Timeline in days")
    complexity = models.FloatField(default=0.0)
    backing_qpt = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    peer_score = models.FloatField(default=0.0)
    engagement_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club_proposals')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        default='in_progress'
    )
    success_rate = models.FloatField(default=0.0)  # Track club's success rate
    feedback = models.TextField(blank=True, null=True)  # Store AI feedback
    
    def evaluate(self):
        try:
            ai_proposal = AIProposal(
                title=self.title,
                description=self.description,
                #proposer_skills=[skill.name for skill in self.created_by.profile.skills.all()],
                #required_skills=[skill.name for skill in self.club.required_skills.all()],
                club_liquidity=float(self.club.qpt_wallet_balance),
                project_budget=float(self.budget),
                expected_timeline=self.timeline,
                market_demand_score=1,
                club_success_rate=self.club.reputation_score,
                risk_level=self.peer_score,
                proposer_reputation_score=self.created_by.profile.reputation_score,
                complexity=self.complexity
            )

            # Get prediction from trained model
            feedback = calculate_score(ai_proposal)
            self.feedback = generate_feedback_report(ai_proposal)

            if "Approved" in feedback:
                self.status = 'approved'
                self.outcome = 'success'
            elif "Needs Adjustment" in feedback:
                self.status = 'pending'
                self.outcome = 'in_progress'
            else:
                self.status = 'rejected'
                self.outcome = 'failure'

        except Exception as e:
            raise ValidationError(_("AI evaluation failed: %(error)s") % {'error': str(e)})

    def save(self, *args, **kwargs):
        if not self.pk:  # Only evaluate on creation, not updates
            self.evaluate()

        # Make sure status and outcome are consistent
        if self.status == 'approved' and self.outcome != 'success':
            raise ValidationError(_("Approved proposals must have a 'success' outcome."))

        if self.status == 'rejected' and self.outcome != 'failure':
            raise ValidationError(_("Rejected proposals must have a 'failure' outcome."))

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    project = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}'
   


class Performance(models.Model):
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='performance')
    success_rate = models.FloatField(default=0.0)
    market_relevance = models.FloatField(default=0.0)
    completion_time = models.IntegerField(default=0)

    class Meta:
        ordering = ['-success_rate']


class Backing(models.Model):
    backer = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    amount = models.FloatField()



class Competition(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    year = models.IntegerField(unique=True)
    winner = models.ForeignKey('Proposal', on_delete=models.SET_NULL, null=True, blank=True)
    prize_pool = models.DecimalField(max_digits=20, decimal_places=2)

    def select_winner(self):
        top_projects = Proposal.objects.filter(
            created_at__year=self.year
        ).order_by('-peer_score', '-engagement_score', '-complexity')[:5]

        if top_projects:
            winner = top_projects[0]
            self.winner = winner
            self.save()

            # Award prize to winning club's wallet
            winner.club.deposit_to_wallet(self.prize_pool)
            winner.club.reputation_score += 10  # Reputation boost for winning a competition
            winner.club.save()
            return winner
        return None