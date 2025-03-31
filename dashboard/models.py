from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
import string
import random
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from cryptography.fernet import Fernet
from django.db.models import Sum, Count, Avg
from club.models import ClubMembership
from datetime import datetime
from django.utils.timezone import now
from django.db.models import Count, F, Q, Sum

# Generate or retrieve your encryption key safely in the settings file
from django.conf import settings

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

MEANS_OF_PAYMENT = (
    ("Mpesa", "Mpesa"),
    ("Cash", "Cash"),
    ("Bank", "Bank")
)

TYPE_OF_PAYMENT = (
    ("Deposit", "Deposit"),
    ("Withdrawal", "Withdrawal"),
    ("Transfer", "Transfer")
)

STATUS_CHOICES = (
    ("Completed", "Completed"),
    ("Pending", "Pending"),
    ("Cancelled", "Cancelled")
)

AREA_OF_INTEREST_CHOICES = (
    ("Farming", "Farming"),
)

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Encrypt the message before saving
        f = Fernet(settings.ENCRYPTION_KEY)
        self.message = f.encrypt(self.message.encode()).decode()
        super(PrivateMessage, self).save(*args, **kwargs)

    def get_decrypted_message(self):
        # Decrypt the message when retrieving it
        f = Fernet(settings.ENCRYPTION_KEY)
        return f.decrypt(self.message.encode()).decode()

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_to', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} is friends with {self.to_user.username}"

class Verify(models.Model):
    phone_no = models.CharField(max_length=10, null=False, blank=False)
    code = models.CharField(max_length=13)
    attempts = models.PositiveIntegerField(default=5)
    times_Day = models.PositiveIntegerField(default=3)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_no
    
class Areas_of_Interest(models.Model):
    area = models.CharField(max_length=10, null=False, blank=False, choices=AREA_OF_INTEREST_CHOICES)


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
    ('None', 'Prefer not to say')
)

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to="profile", blank=True, null=True)
    phone_no = models.CharField(max_length=10, unique=True)
    county = models.CharField(max_length=100, default="Nairobi")
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default="None")
    code = models.CharField(max_length=8, default=id_generator)
    profession = models.CharField(max_length=100, default="Engineer")
    referrer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="referred_users", null=True, blank=True)
    referred_friends = models.ManyToManyField(User, related_name="referrals", blank=True)
    followers = models.ManyToManyField(User, related_name="followers", blank=True)
    bio = models.TextField(null=True, blank=True)
    funds = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    shares = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_pro = models.BooleanField(default=False)
    reputation_score = models.IntegerField(default=1)
    points = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    is_admin = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, related_name="profiles", blank=True)

    def notifications_count(self) -> int:
        """Returns the count of notifications for the user."""
        return self.user.notifications.filter(is_read=False).count()

    def name(self) -> str:
        return self.user.get_full_name()

    def account_age(self) -> int:
        """Calculate account age in months."""
        if self.user.date_joined:
            return (now() - self.user.date_joined).days // 30
        return 0
    
    def user_clubs(self):
        """Returns a list of club categories the user belongs to."""
        from .models import ClubMembership  # Import only when needed to avoid circular import

        clubs = ClubMembership.objects.filter(user=self.user).select_related('club__category')
        return [c.club.category for c in clubs]

    def rank_score(self) -> float:
        """
        Calculates a score to rank users based on:
            - points (weight = 0.5)
            - funds (weight = 0.1)
            - number of referred friends (weight = 0.2)
        """
        points_weight = 0.5
        funds_weight = 0.1
        referrals_weight = 0.2

        return float(round(
            float(self.points) * points_weight +
            float(self.funds) * funds_weight +
            self.referred_friends.count() * referrals_weight,
            2
        ))

    def rank(self) -> int | None:
        """
        Calculates the user's rank compared to other profiles based on their rank score.
        Uses direct query-based ranking for better performance.
        """
        profiles = Profile.objects.annotate(
            rank_score=(
                F("points") * 0.5 +
                F("funds") * 0.1 +
                Count("referred_friends") * 0.2
            )
        ).order_by('-rank_score')

        # Get rank using position
        ranked_profiles = list(profiles.values_list('id', flat=True))
        try:
            return ranked_profiles.index(self.id) + 1
        except ValueError:
            return None

    @classmethod
    def ranked_profiles(cls):
        """
        Returns a queryset of profiles sorted by rank score in descending order.
        Uses annotation for direct sorting.
        """
        return cls.objects.annotate(
            rank_score=(
                F("points") * 0.5 +
                F("funds") * 0.1 +
                Count("referred_friends") * 0.2
            )
        ).order_by('-rank_score')

    def __str__(self):
        return self.name()


    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_OF_PAYMENT, default="Deposit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    reference = models.CharField(max_length=12)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.amount}"

    @classmethod
    def total_amount_by_type(cls, transaction_type):
        """
        Calculate the total amount for a given transaction type.
        """
        return cls.objects.filter(type=transaction_type, status="Completed").aggregate(total=Sum('amount'))['total'] or 0

    @classmethod
    def count_transactions_by_type(cls, transaction_type):
        """
        Count the number of transactions for a given type.
        """
        return cls.objects.filter(type=transaction_type).count()

    @classmethod
    def average_amount_by_type(cls, transaction_type):
        """
        Calculate the average transaction amount for a given type.
        """
        return cls.objects.filter(type=transaction_type, status="Completed").aggregate(average=Avg('amount'))['average'] or 0

    @classmethod
    def transaction_summary(cls):
        """
        Get a summary of all transaction types with their total amounts and counts.
        """
        summary = {}
        for transaction_type, _ in TYPE_OF_PAYMENT:
            summary[transaction_type] = {
                "total_amount": cls.total_amount_by_type(transaction_type),
                "count": cls.count_transactions_by_type(transaction_type),
                "average_amount": cls.average_amount_by_type(transaction_type)
            }
        return summary
    
class Contribute(models.Model):
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    phone = models.CharField(max_length=10)
    means = models.CharField(max_length=20, choices=MEANS_OF_PAYMENT, default="Mpesa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    reference = models.CharField(max_length=12)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.phone + " -> " + self.amount + " -> " + self.reference
    
class Funding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    phone = models.CharField(max_length=10)
    means = models.CharField(max_length=20, choices=MEANS_OF_PAYMENT, default="Mpesa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    reference = models.CharField(max_length=12)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.user.first_name + " -> " + self.amount + " -> " + self.reference
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.user.email

def get_deadline():
    return datetime.now() + timedelta(days=30)

class Loan(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    due = models.DateTimeField(default=get_deadline)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.user.username


class Mentorship(models.Model):
    title = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    mentors = models.ManyToManyField(User, related_name='mentorships')

    def __str__(self):
        return self.title


class Success_Story(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    story = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.title
    
class Message(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        return self.name
    
class Blog(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    story = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.title
    
class Point_Tracker(models.Model):
    title = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    points = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
    
    def __str__(self):
        return self.title
