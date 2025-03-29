from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
from django.utils.timezone import now
from club.models import Club

# Possible talent categories
TALENT_CATEGORIES = [
    ('music', 'Music'),
    ('dance', 'Dance'),
    ('acting', 'Acting'),
    ('sports', 'Sports'),
    ('fashion', 'Fashion'),
    ('art', 'Art'),
    ('comedy', 'Comedy'),
    ('influencing', 'Influencing'),
]

BOOKING_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
]

class Talent(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='talents')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='talent_profile')
    name = models.CharField(max_length=255)
    bio = models.TextField()
    category = models.CharField(max_length=50, choices=TALENT_CATEGORIES)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    profile_image = models.ImageField(upload_to='talent_profiles/', null=True, blank=True)
    video_demo = models.FileField(upload_to='talent_videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.name} ({self.club.name})"
    
    class Meta:
        ordering = ['-rating']

    def calculate_rating(self):
        reviews = self.reviews.all()
        if reviews:
            self.rating = sum(review.rating for review in reviews) / reviews.count()
            self.total_reviews = reviews.count()
            self.save()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.duration_hours * self.talent.price_per_hour
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} booked {self.talent.name} on {self.date.strftime('%Y-%m-%d')}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.user.username} - {self.amount} ({self.status})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=0)  # 1-5 scale
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.talent.name} ({self.rating}/5)"

    class Meta:
        unique_together = ['user', 'talent']  # A user can only leave one review per talent

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} follows {self.talent.name}"

    class Meta:
        unique_together = ['user', 'talent']

