from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
import string
import random
from datetime import datetime, timedelta

CATEGORIES = [
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

class JobPosition(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default="education")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100, default="Remote")
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    is_open = models.BooleanField(default=True)

    class Meta:
        ordering = ("-posted_date",)

    def applicants(self):
        return JobApplication.objects.filter(job_position=self)

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='applications')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ("Submitted", "Submitted"),
            ("Under Review", "Under Review"),
            ("Accepted", "Accepted"),
            ("Rejected", "Rejected"),
        ),
        default="Submitted"
    )

    class Meta:
        ordering = ("-applied_date",)

    def __str__(self):
        return f"{self.user.username} - {self.job_position.title}"
