from django.db import models
from django.contrib.auth.models import User
import uuid

class PointTransaction(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    amount = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=[('transfer', 'Transfer'), ('sale', 'Sale')])
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver or 'Market'} - {self.amount} Points"


class PointTransfer(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transfers_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transfers_received')
    amount = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} | {self.amount} Points"


class PointSale(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('available', 'Available'), ('sold', 'Sold'), ('canceled', 'Canceled')], default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - {self.points} Points for {self.price} KES"
