from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Profile
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from django.utils import timezone
from datetime import datetime, timedelta
from uuid import uuid4
import uuid
from club.models import Club
def gen_uuid():
    return uuid4()

STATUS_CHOICES = (
    ("Approved", "Approved"),
    ("Pending", "Pending"),
    ("Rejected", "Rejected")
)

class Project(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_owner')
    description = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="Pending")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name='projects')

    class Meta:
        ordering = ("-start_date",)

    def save(self, *args, **kwargs):
        profile = Profile.objects.get(user=self.user)
        if profile.points < 100:  # Check if user has at least 100 points
            raise ValueError("Insufficient points to propose this project.")
        profile.points -= 10  # Deduct 10 points for each project proposal
        profile.save()
        super().save(*args, **kwargs)

    # Project Statistics Methods
    def participant_count(self):
        """Returns the total number of participants in the project."""
        return self.participants.count()

    def progress(self):
        """Returns the progress of the project as a percentage."""
        if not self.end_date:
            return 0
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (timezone.now().date() - self.start_date).days
        return min(100, int((elapsed_days / total_days) * 100)) if total_days > 0 else 0

    def duration(self):
        """Returns the duration of the project in days."""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    def pending_projects(cls):
        """Returns the total number of pending projects."""
        return cls.objects.filter(status="Pending").count()

    def completed_projects(cls):
        """Returns the total number of completed projects."""
        return cls.objects.filter(is_completed=True).count()


    def __str__(self):
        return self.title

    
class ChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}'
    

class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
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
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='proposals')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
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