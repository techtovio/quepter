from django.db import models
from django.contrib.auth.models import User
import uuid

class Competition(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Challenge(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    points_awarded = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.competition.name}"

class UserChallengeParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    class Meta:
        ordering = ['-points']

class Badge(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_awarded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Reward(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    points_required = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import User
import uuid

class CrowdFundingChallenge(models.Model):
    # UUID for uniquely identifying each challenge
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Title and description of the challenge
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Funding details
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Example: $10,000.00
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Money raised so far

    # Duration
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()  # Deadline for the funding challenge

    # Owner of the challenge (User who created it)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crowdfunding_challenges')

    # Whether the challenge is active or not
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']  # Newer challenges appear first
        verbose_name = "Crowd Funding Challenge"
        verbose_name_plural = "Crowd Funding Challenges"

class Transaction(models.Model):
    # UUID for uniquely identifying each transaction
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Reference to the funding challenge
    challenge = models.ForeignKey(CrowdFundingChallenge, on_delete=models.CASCADE, related_name='transactions')

    # User making the transaction
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')

    # Amount of the transaction
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Timestamp of when the transaction was made
    transaction_date = models.DateTimeField(auto_now_add=True)

    # Optional: any notes or messages from the user contributing
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction by {self.user} for {self.challenge.title}"

    class Meta:
        ordering = ['-transaction_date']  # Newest transactions appear first
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
