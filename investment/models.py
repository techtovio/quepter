from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from uuid import uuid4

def gen_uuid():
    return uuid4()

CATEGORY_CHOICES = [
    ('education', 'Education & Learning'),
    ('business', 'Business & Entrepreneurship'),
    ('technology', 'Technology & Innovation'),
    ('creative', 'Creative Arts & Media'),
    ('health', 'Health & Wellness'),
    ('sports', 'Sports & Recreation'),
    ('finance', 'Finance & Investment'),
    ('social', 'Social Impact & Community Service'),
    ('environment', 'Environment & Sustainability'),
]

INVITES_CHOICES = [
    ('5','must have referred at least 5 members'),
    ('10','must have referred at least 10 members'),
    ('15','must have referred at least 15 members'),
    ('20','must have referred at least 20 members'),
    ('30','must have referred at least 30 members'),
]

ACCOUNT_AGE_CHOICES = [
    ('2','must have been active in the respective club for over 2 months'),
    ('5','must have been active in the respective club for over 5 months'),
    ('10','must have been active in the respective club for over 10 months'),
    ('15','must have been active in the respective club for over 15 months'),
    ('20','must have been active in the respective club for over 20 months'),
]

class InvestmentOpportunity(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="funding", blank=True, null=True)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=1000, default="Agribusiness", choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=100)
    min_points_required = models.PositiveIntegerField(default=0)
    account_age_requirements = models.CharField(max_length=100, choices=ACCOUNT_AGE_CHOICES, default='2')
    invites_required = models.CharField(max_length=100, choices=INVITES_CHOICES, default='5')
    club_required = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='business')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    class Meta:
        ordering = ("-timestamp",)

    def requests(self):
        return MemberInvestmentRequest.objects.filter(project=self)

    def __str__(self):
        return self.title

class MemberInvestmentRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(InvestmentOpportunity, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    application_text = models.TextField()
    points = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"

class MentorshipProgram(models.Model):
    mentor_name = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    description = models.TextField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.title
