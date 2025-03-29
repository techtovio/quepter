import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from hiero_sdk_python import (
    Client,
    Network,
    AccountId,
    PrivateKey,
    AccountCreateTransaction,
    TokenAssociateTransaction,
    ResponseCode
)
from django.core.exceptions import ImproperlyConfigured
import base64
load_dotenv()

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

STATUS_CHOICES = (
    ("Completed", "Completed"),
    ("Pending", "Pending"),
    ("Cancelled", "Cancelled")
)


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
    annual_return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    qpt_wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    app_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    public_key = models.CharField(max_length=500, null=True, blank=True)
    qpt_private_key = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Encrypt private keys before saving."""
        if self.qpt_private_key:
            key_str = str(self.qpt_private_key)  # Ensure it's a string
            if not key_str.startswith("gAAAA"):  # Avoid double encryption
                self.qpt_private_key = self.encrypt_key(key_str)
        super().save(*args, **kwargs)

    def encrypt_key(self, key: str) -> str:
        """
        Encrypt the private key using Fernet.
        """
        try:
            secret_key = os.getenv('SECRET_KEY')
            if not secret_key:
                raise ValueError("Missing SECRET_KEY in environment variables")
            
            # Ensure the secret key is 32 bytes long
            key_bytes = secret_key.encode()
            key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
            f = Fernet(key_base64)
            return f.encrypt(key.encode()).decode()
        except Exception as e:
            raise ValueError(f"Encryption error: {e}")

    def decrypt_key(self) -> str:
        """
        Decrypt the private key using Fernet.
        """
        try:
            secret_key = os.getenv('SECRET_KEY')
            if not secret_key:
                raise ValueError("Missing SECRET_KEY in environment variables")
            
            # Ensure the secret key is 32 bytes long
            key_bytes = secret_key.encode()
            key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
            f = Fernet(key_base64)
            return f.decrypt(self.qpt_private_key.encode()).decode()
        except Exception as e:
            raise ValueError(f"Decryption error: {e}")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['-reputation_score']

    def member_count(self) -> int:
        """Return the number of members in the club."""
        return self.members.count()

    def calculate_annual_returns(self) -> float:
        """Calculate and return the annual returns based on total contributions and rate."""
        return (self.total_contributions * self.annual_return_rate) / 100

    


# --------------------------- CLUB MEMBERSHIP ---------------------------
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

# --------------------------- CLUB BROADCAST ---------------------------
class ClubBroadcast(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Broadcast in {self.club.name} at {self.created_at}"

# --------------------------- CLUB TRANSACTIONS ---------------------------
class ClubTransaction(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)  # Example: "Weekly Contribution", "Project Backing"
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Completed")

    def __str__(self):
        return f"{self.club.name} - {self.transaction_type} - {self.amount} QPT"

# --------------------------- CLUB CONTRIBUTION ---------------------------
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
        membership = ClubMembership.objects.get(user=self.user, club=self.club)
        membership.total_contributed += self.amount
        membership.save()

        # Update club's total contributions
        self.club.total_contributions += self.amount
        self.club.save()

        # Convert to QPT and update club's QPT wallet
        qpt_value = int(self.amount) // 10  # Example: 1 QPT = 10 KES
        if qpt_value > 0:
            self.club.total_qpt += qpt_value
            self.club.qpt_wallet_balance += qpt_value

            # Register the QPT transaction
            ClubTransaction.objects.create(
                club=self.club,
                amount=qpt_value,
                transaction_type="Weekly Contribution",
                status="Completed"
            )

            self.club.save()

        super().save(*args, **kwargs)
