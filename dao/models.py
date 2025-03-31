from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DAO(models.Model):
    name = models.CharField(max_length=100, default="Quepter Youth Hub")
    description = models.TextField(default="A decentralized community for youth innovators.")
    treasury_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def member_count(self):
        return self.members.count()

    @property
    def proposal_count(self):
        return self.proposals.count()

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dao_memberships')
    dao = models.ForeignKey(DAO, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    voting_power = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)  # Equal voting power

    class Meta:
        unique_together = ('user', 'dao')

class Proposal(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]
    
    dao = models.ForeignKey(DAO, on_delete=models.CASCADE, related_name='dao_proposals')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dao_creator')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=7))

    @property
    def votes_for(self):
        return self.votes.filter(vote='for').count()

    @property
    def votes_against(self):
        return self.votes.filter(vote='against').count()

class Vote(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.CharField(max_length=10, choices=[('for', 'For'), ('against', 'Against')])
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('proposal', 'voter')