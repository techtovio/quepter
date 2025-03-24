from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from uuid import uuid4

class LeadershipPosition(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    points_required = models.IntegerField(default=0)
    is_open = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(LeadershipPosition, on_delete=models.CASCADE)
    manifesto = models.TextField()
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    points = models.IntegerField(default=0)
    referral_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} for {self.position.title}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    vote_hash = models.UUIDField(default=uuid4, unique=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote by {self.user.username} for {self.candidate.user.username}"

class Blockchain(models.Model):
    previous_hash = models.CharField(max_length=64)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    block_hash = models.CharField(max_length=64, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Block {self.vote.id}"
