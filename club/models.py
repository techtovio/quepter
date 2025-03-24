from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
import uuid
from django.utils.timezone import now, timedelta

# Possible categories for clubs
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

# Terms and conditions for each category
CATEGORY_TERMS = {
    'education': "Focuses on academic discussions, online courses, and study groups.",
    'business': "Encourages startup ideas, business strategies, and entrepreneurship networking.",
    'technology': "Explores tech trends, software development, and innovation in AI and machine learning.",
    'creative': "Promotes art, music, media production, and other creative endeavors.",
    'health': "Centers around mental and physical wellness, fitness, and health resources.",
    'sports': "Engages in sports activities, discussions, and events.",
    'finance': "Covers investment strategies, financial literacy, and cryptocurrency.",
    'social': "Focuses on community service, volunteering, and social impact projects.",
    'environment': "Dedicated to environmental awareness, conservation, and sustainability projects."
}

STATUS_CHOICES = (
    ("Completed", "Completed"),
    ("Pending", "Pending"),
    ("Cancelled", "Cancelled")
)

# Club model to represent each club
class Club(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    terms_and_conditions = models.TextField()
    image = models.ImageField(upload_to='club_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, through='ClubMembership', related_name='clubs')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    joining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    weekly_contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    balance = models.FloatField(default=0)
    reputation_score = models.FloatField(default=0.0)
    total_qpt = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    annual_return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # Example: 10% annual return

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-reputation_score']
    
    # Methods for club statistics
    def member_count(self):
        return self.members.count()

    def calculate_annual_returns(self):
        return (self.total_contributions * self.annual_return_rate) / 100

    def benefits(self):
        return [
            "Access to exclusive projects and events.",
            "Annual dividends based on contributions.",
            "Networking opportunities with other members.",
            "Priority consideration for club initiatives.",
            "Mentorship and training programs.",
        ]

# Model for a club membership to track user memberships and payments
class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    has_paid_membership_fee = models.BooleanField(default=False)
    total_contributed = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} in {self.club.name}"
    
    def loyalty_points(self):
        return self.total_contributed // 10

# Model for broadcasting messages to club members
class ClubBroadcast(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Broadcast in {self.club.name} at {self.created_at}"

# Contribution model to track individual contributions
class ClubContribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Completed")
    points_awarded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.club.name} - {self.amount} KES on {self.date}"

    def save(self, *args, **kwargs):
        # Update user's total contributions and loyalty points
        membership = ClubMembership.objects.get(user=self.user, club=self.club)
        membership.total_contributed += int(self.amount)
        membership.save()
        print(int(self.amount))

        # Update club's total contributions and weekly contributions
        self.club.total_contributions += int(self.amount)
        self.club.save()

        super().save(*args, **kwargs)